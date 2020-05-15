import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from legacy.models import PatientNumber, LegacySkinPrickTest
from rbhl.models import SpecificSkinPrickTest

from ..utils import to_date, to_float, to_int


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def build_legacy_skin_prick_test(self, file_name):
        LegacySkinPrickTest.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(file_name, encoding="utf-8-sig") as f:
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
                LegacySkinPrickTest(
                    patient=patient,
                    created=timezone.now(),
                    specific_sp_testnum=to_int(row["Specific_sp_testnum"]),
                    spt=row["SPT"],
                    wheal=to_float(row["Wheal"]),
                    test_date=to_date(row["Testdate"]),
                )
            )

        LegacySkinPrickTest.objects.bulk_create(tests)
        msg = "Created {} Skin Prick Tests".format(len(tests))
        self.stdout.write(self.style.SUCCESS(msg))

    @transaction.atomic()
    def convert_legacy_skin_prick_tests(self):
        skin_prick_tests = []
        for legacy in LegacySkinPrickTest.objects.all():
            episode = legacy.patient.episode_set.get()
            specific_skin_prick = SpecificSkinPrickTest(
                episode=episode
            )
            specific_skin_prick.specific_sp_testnum = legacy.specific_sp_testnum
            specific_skin_prick.spt = legacy.spt
            specific_skin_prick.wheal = legacy.wheal
            specific_skin_prick.test_date = legacy.test_date

            skin_prick_tests.append(specific_skin_prick)

        SpecificSkinPrickTest.objects.bulk_create(skin_prick_tests)

    def handle(self, *args, **kwargs):
        self.build_legacy_skin_prick_test(kwargs["file_name"])
        self.convert_legacy_skin_prick_tests()
