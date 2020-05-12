import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import PatientNumber, LegacyRoutineSPT

from ..utils import to_float


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def handle(self, *args, **options):
        LegacyRoutineSPT.objects.all().delete()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
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
