
import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone

from legacy.models import RoutineSPT, PatientNumber


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic()
    def handle(self, *args, **options):
        RoutineSPT.objects.all().delete()

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

            if not row["asp_fumigatus"]:
                msg = "Skipped {}, empty asp_fumigatus".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            if not row["cat"]:
                msg = "Skipped {}, empty cat".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            if not row["d_pter"]:
                msg = "Skipped {}, empty d_pter".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            if not row["neg_control"]:
                msg = "Skipped {}, empty neg_control".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            if not row["grass_pollen"]:
                msg = "Skipped {}, empty grass_pollen".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            if not row["pos_control"]:
                msg = "Skipped {}, empty pos_control".format(row["Patient_num"])
                self.stderr.write(self.style.ERROR(msg))
                continue

            tests.append(
                RoutineSPT(
                    patient=patient,
                    created=timezone.now(),
                    neg_control=float(row["neg_control"]),
                    pos_control=float(row["pos_control"]),
                    asp_fumigatus=float(row["asp_fumigatus"]),
                    grass_pollen=float(row["grass_pollen"]),
                    cat=float(row["cat"]),
                    d_pter=float(row["d_pter"]),
                )
            )

        RoutineSPT.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Routine SPTs".format(len(tests)))
        )
