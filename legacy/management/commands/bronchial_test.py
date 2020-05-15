import csv
from datetime import datetime

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import LegacyBronchialTest, PatientNumber
from rbhl.models import BronchialTest


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def build_date_of_challenge(self, raw):
        if not raw:
            return

        try:
            dt = datetime.strptime(raw, "%d-%b-%y")
        except ValueError:
            return

        return timezone.make_aware(dt)

    def build_last_exposed(self, raw):
        """
        Build a datetime object from the passed last_exposed data.

        The Last_exposed field uses non-zero-padded days and months.  Not all
        platforms support the lack of zero padding so handle that here and
        build a datetime from the outcome.
        """
        if not raw:
            return

        try:
            day, month, year = raw.split(" ")
        except ValueError:
            msg = "Unable to parse: {}".format(raw)
            self.stderr.write(self.style.ERROR(msg))
            return

        fixed_string = "{} {} {}".format(
            day.zfill(2),
            month.zfill(2),
            year.zfill(2),
        )

        try:
            dt = datetime.strptime(fixed_string, "%d %m %y")
        except ValueError:
            msg = "Unable to parse: {}".format(raw)
            self.stderr.write(self.style.ERROR(msg))
            return

        return timezone.make_aware(dt)

    @transaction.atomic()
    def build_legacy_bronchial_test(self, file_name):
        LegacyBronchialTest.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(file_name, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        self.stdout.write(self.style.SUCCESS("Importing bronchial tests"))
        tests = []
        for row in rows:
            try:
                p_num = PatientNumber.objects.get(value=row["Patient_num"])
                patient = p_num.patient
            except PatientNumber.DoesNotExist:
                msg = "Unknown Patient: {}".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            last_exposed = self.build_last_exposed(row["Last_exposed"])
            date_of_challenge = self.build_date_of_challenge(
                row["Date of Challenge"]
            )

            tests.append(
                LegacyBronchialTest(
                    patient=patient,
                    created=timezone.now(),
                    bronchial_num=row["Bronchial_num"],
                    substance=row["Substance"],
                    last_exposed=last_exposed,
                    duration_exposed=row["Duration_exposure"],
                    date_of_challenge=date_of_challenge,
                    foo=row["Type"],
                    other_type=row["OtherType"],
                    other=row["Other"],
                    baseline_pc290=row["BaselinePC20"],
                    lowest_pc20=row["LowestPC20"],
                )
            )

        LegacyBronchialTest.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Bronchial Tests".format(len(tests)))
        )

    @transaction.atomic()
    def convert_bronchial_tests(self):
        to_create = []
        for legacy_bronchial_test in LegacyBronchialTest.objects.all():
            episode = legacy_bronchial_test.patient.episode_set.get()
            bronchial_test = BronchialTest(
                episode=episode,
            )

            bronchial_test.test_num = legacy_bronchial_test.bronchial_num
            bronchial_test.substance = legacy_bronchial_test.substance
            bronchial_test.last_exposed = legacy_bronchial_test.last_exposed
            bronchial_test.duration_exposed = legacy_bronchial_test.duration_exposed
            bronchial_test.date_of_challenge = legacy_bronchial_test.date_of_challenge
            if legacy_bronchial_test.other:
                bronchial_test.result = legacy_bronchial_test.other
            else:
                bronchial_test.result = legacy_bronchial_test.foo

            if legacy_bronchial_test.other_type:
                bronchial_test.response_type = legacy_bronchial_test.other_type
            bronchial_test.baseline_pc20 = legacy_bronchial_test.baseline_pc290
            bronchial_test.lowest_pc20 = legacy_bronchial_test.lowest_pc20
            to_create.append(bronchial_test)

        BronchialTest.objects.bulk_create(to_create)

    def handle(self, *args, **options):
        self.build_legacy_bronchial_test(options["file_name"])
        self.convert_bronchial_tests()
