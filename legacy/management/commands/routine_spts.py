
import csv

from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from opal.models import Patient

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

        tests = []
        for row in rows:
            try:
                p_num = PatientNumber.objects.get(value=row["Patient_num"])
                patient = p_num.patient
            except PatientNumber.DoesNotExist:
                patient = Patient.objects.create()
                patient.patientnumber_set.get().update_from_dict(
                    {"created": timezone.now(), "value": row["Patient_num"]}, user=None
                )

            tests.append(
                RoutineSPT(
                    patient=patient,
                    created=timezone.now(),
                    neg_control=row["neg_control"],
                    pos_control=row["pos_control"],
                    asp_fumigatus=row["asp_fumigatus"],
                    grass_pollen=row["grass_pollen"],
                    cat=row["cat"],
                    dog=row["dog"],
                    d_pter=row["d_pter"],
                    alternaria=row["alternaria"],
                    clad=row["clad"],
                )
            )

        RoutineSPT.objects.bulk_create(tests)
        self.stdout.write(
            self.style.SUCCESS("Created {} Routine SPTs".format(len(tests)))
        )
