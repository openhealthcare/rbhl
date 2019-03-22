import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import BronchialTest, PatientNumber


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def handle(self, *args, **options):
        BronchialTest.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        tests = []
        for row in rows:
            try:
                p_num = PatientNumber.objects.get(value=row["Patient_num"])
                patient = p_num.patient
            except PatientNumber.DoesNotExist:
                msg = "Unknown Patient: {}".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            tests.append(
                BronchialTest(
                    patient=patient,
                    created=timezone.now(),
                    bronchial_num=row["Bronchial_num"],
                    substance=row["Substance"],
                    last_exposed=row["Last_exposed"],
                    duration_exposed=row["Duration_exposure"],
                    date_of_challenge=row["Date of Challenge"],
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
