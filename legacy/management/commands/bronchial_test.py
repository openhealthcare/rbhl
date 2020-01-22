import csv
from datetime import datetime

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import BronchialTest, PatientNumber


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
    def handle(self, *args, **options):
        BronchialTest.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
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
                BronchialTest(
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

        BronchialTest.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Bronchial Tests".format(len(tests)))
        )
