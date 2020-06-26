import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient
from legacy.models import PatientNumber, LegacySkinPrickTest
from plugins.lab.models import SkinPrickTest

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
        msg = "Created {} Legacy Skin Prick Tests".format(len(tests))
        self.stdout.write(self.style.SUCCESS(msg))

    def get_antihistimines(self, patient):
        diagnostic_testing = patient.diagnostictesting_set.all()
        if len(diagnostic_testing):
            return diagnostic_testing[0].antihistamines

    @transaction.atomic()
    def convert_legacy_skin_prick_tests(self):
        skin_prick_tests = []
        qs = Patient.objects.exclude(legacyskinpricktest=None)
        qs = qs.prefetch_related(
            "legacyskinpricktest_set",
            "diagnosticoutcome_set",
            "diagnostictesting_set",
        )
        for patient in qs:
            antihistamines = self.get_antihistimines(patient)
            for legacy in patient.legacyskinpricktest_set.all():

                # there are 181 patients with no spt, they also
                # have not wheal
                if not legacy.spt:
                    continue

                dt = legacy.test_date

                skin_prick_tests.append(SkinPrickTest(
                    substance=legacy.spt,
                    date=dt,
                    wheal=legacy.wheal,
                    patient=patient,
                    antihistamines=antihistamines,
                ))

        SkinPrickTest.objects.bulk_create(skin_prick_tests)
        msg = "Created {} SkinPrickTests from LegacySkinPrickTests".format(
            len(skin_prick_tests)
        )
        self.stdout.write(self.style.SUCCESS(msg))

    def handle(self, *args, **kwargs):
        self.build_legacy_skin_prick_test(kwargs["file_name"])
        self.convert_legacy_skin_prick_tests()
