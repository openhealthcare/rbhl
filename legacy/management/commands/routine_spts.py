import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient
from plugins.lab.models import SkinPrickTest

from legacy.models import PatientNumber, RoutineSPT

from ..utils import to_float


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def build_routine_spts(self, file_name):
        RoutineSPT.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(file_name, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        self.stdout.write(self.style.SUCCESS("Importing Routine SPTs"))
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
                RoutineSPT(
                    patient=patient,
                    created=timezone.now(),
                    neg_control=to_float(row["neg_control"]),
                    pos_control=to_float(row["pos_control"]),
                    asp_fumigatus=to_float(row["asp_fumigatus"]),
                    grass_pollen=to_float(row["grass_pollen"]),
                    cat=to_float(row["cat"]),
                    d_pter=to_float(row["d_pter"]),
                )
            )

        RoutineSPT.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Routine SPTs".format(len(tests)))
        )

    def get_antihistimines(self, patient):
        diagnostic_testing = patient.diagnostictesting_set.all()
        if len(diagnostic_testing):
            return diagnostic_testing[0].antihistimines

    @transaction.atomic()
    def convert_routine_spts(self):
        skin_prick_tests = []
        qs = Patient.objects.exclude(routinespt=None)
        qs = qs.prefetch_related(
            "routinespt_set",
            "diagnosticoutcome_set",
            "diagnostictesting_set",
            "otherfields_set",
        )
        for patient in qs:
            antihistimines = self.get_antihistimines(patient)
            attendance_date = patient.otherfields_set.all()[0].attendance_date_as_date()

            for legacy in patient.routinespt_set.all():
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.NEG_CONTROL,
                    wheal=legacy.neg_control,
                    date=attendance_date,
                    patient=patient
                ))
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.POS_CONTROL,
                    wheal=legacy.pos_control,
                    date=attendance_date,
                    patient=patient
                ))
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.ASP_FUMIGATUS,
                    wheal=legacy.asp_fumigatus,
                    date=attendance_date,
                    patient=patient
                ))
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.GRASS_POLLEN,
                    wheal=legacy.grass_pollen,
                    date=attendance_date,
                    patient=patient
                ))
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.CAT,
                    wheal=legacy.cat,
                    date=attendance_date,
                    patient=patient
                ))
                skin_prick_tests.append(SkinPrickTest(
                    antihistimines=antihistimines,
                    substance=SkinPrickTest.HOUSE_DUST_MITE,
                    wheal=legacy.d_pter,
                    date=attendance_date,
                    patient=patient
                ))
        SkinPrickTest.objects.bulk_create(skin_prick_tests)
        msg = "Created {} SkinPrickTests from RoutineSPTs".format(
            len(skin_prick_tests)
        )
        self.stdout.write(self.style.SUCCESS(msg))

    def handle(self, *args, **options):
        self.build_routine_spts(options["file_name"])
        self.convert_routine_spts()
