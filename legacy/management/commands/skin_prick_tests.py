import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient
from legacy.models import PatientNumber, LegacySkinPrickTest
from rbhl.models import DiagnosticTest

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
    def build_skin_prick_test(self, patient):
        diagnostic_testing_set = patient.diagnostictesting_set.all()
        skin_prick_tests = patient.legacyskinpricktest_set.all()
        episode = patient.episode_set.get()
        SKIN_PRICK_TEST_FIELDS = [
            "antihistimines",
            "skin_prick_test",
            "atopic",
            "specific_skin_prick",
            "serum_antibodies"
        ]

        for legacy_diagnostic_testing in diagnostic_testing_set:
            if any([
                getattr(legacy_diagnostic_testing, i) for i in SKIN_PRICK_TEST_FIELDS
            ]):
                diagnostic_test_args = {
                    "episode": episode,
                    "test_type": DiagnosticTest.SKIN_PRICK_TEST,
                }
                for field in SKIN_PRICK_TEST_FIELDS:
                    if field == "skin_prick_test":
                        continue
                    if field == "serum_antibodies":
                        immunology_oem = legacy_diagnostic_testing.serum_antibodies
                        diagnostic_test_args["immunology_oem"] = immunology_oem
                    else:
                        field_value = getattr(legacy_diagnostic_testing, field)
                        diagnostic_test_args[field] = field_value

                if not skin_prick_tests:
                    return [DiagnosticTest(**diagnostic_test_args)]
                else:
                    diagnosis_tests = []
                    for skin_prick_test in skin_prick_tests:
                        for field in [
                            "specific_sp_testnum", "spt", "wheal", "test_date"
                        ]:
                            field_value = getattr(skin_prick_test, field)
                            diagnostic_test_args[field] = field_value
                        diagnosis_tests.append(
                            DiagnosticTest(**diagnostic_test_args)
                        )

                    return diagnosis_tests
        return []

    @transaction.atomic()
    def convert_legacy_skin_prick_tests(self):
        patients = Patient.objects.exclude(diagnostictesting=None)
        patients = patients.prefetch_related(
            "diagnostictesting_set", "legacyskinpricktest_set"
        )
        diagnosis_tests = []
        for patient in patients:
            diagnosis_tests.extend(self.build_skin_prick_test(patient))
        DiagnosticTest.objects.bulk_create(diagnosis_tests)

    def handle(self, *args, **kwargs):
        self.build_legacy_skin_prick_test(kwargs["file_name"])
        self.convert_legacy_skin_prick_tests()
