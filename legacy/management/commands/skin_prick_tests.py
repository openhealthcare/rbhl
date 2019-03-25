import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import PatientNumber, SkinPrickTest

from ..utils import to_date, to_float, to_int


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def handle(self, *args, **options):
        SkinPrickTest.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        self.stdout.write(self.style.SUCCESS("Importing Skin Prick Tests"))
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
                SkinPrickTest(
                    patient=patient,
                    created=timezone.now(),
                    specific_sp_testnum=to_int(row["Specific_sp_testnum"]),
                    spt=row["SPT"],
                    wheal=to_float(row["Wheal"]),
                    test_date=to_date(row["Testdate"]),
                )
            )

        SkinPrickTest.objects.bulk_create(tests)
        msg = "Created {} Skin Prick Tests".format(len(tests))
        self.stdout.write(self.style.SUCCESS(msg))
