import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient
from rbhl.models import SkinPrickTest

from legacy.models import PatientNumber, LegacyRoutineSPT

from ..utils import to_float


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def build_routine_spts(self, file_name):
        LegacyRoutineSPT.objects.all().delete()

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
                LegacyRoutineSPT(
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

        LegacyRoutineSPT.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Routine SPTs".format(len(tests)))
        )

    def get_diagnosis_date(self, patient):
        diagnostic_outcome = patient.diagnosticoutcome_set.all()
        if len(diagnostic_outcome):
            return diagnostic_outcome[0].diagnosis_date

    def get_antihistimines(self, patient):
        diagnostic_testing = patient.diagnostictesting_set.all()
        if len(diagnostic_testing):
            return diagnostic_testing[0].antihistimines

    @transaction.atomic()
    def convert_routine_spts(self):
        skin_prick_tests = []
        qs = Patient.objects.exclude(legacyroutinespt=None)
        qs = qs.prefetch_related(
            "legacyroutinespt_set",
            "diagnosticoutcome_set",
            "diagnostictesting_set",
            "episode_set",
        )
        for patient in qs:
            diagnosis_date = self.get_diagnosis_date(patient)
            antihistimines = self.get_antihistimines(patient)
            episode = patient.episode_set.all()[0]

            for legacy in patient.legacyroutinespt_set.all():
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.NEG_CONTROL,
                    wheal=legacy.neg_control,
                    episode=episode
                ))
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.POS_CONTROL,
                    wheal=legacy.pos_control,
                    episode=episode
                ))
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.ASP_FUMIGATUS,
                    wheal=legacy.asp_fumigatus,
                    episode=episode
                ))
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.GRASS_POLLEN,
                    wheal=legacy.grass_pollen,
                    episode=episode
                ))
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.CAT,
                    wheal=legacy.cat,
                    episode=episode
                ))
                skin_prick_tests.append(SkinPrickTest(
                    date=diagnosis_date,
                    antihistimines=antihistimines,
                    spt=SkinPrickTest.HOUSE_DUST_MITE,
                    wheal=legacy.d_pter,
                    episode=episode
                ))
        SkinPrickTest.objects.bulk_create(skin_prick_tests)

    def handle(self, *args, **options):
        self.build_routine_spts(options["file_name"])
        self.convert_routine_spts()
