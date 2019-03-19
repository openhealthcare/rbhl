"""
Management command to import all data to the database
"""
import csv
from datetime import date, datetime

from django.core.management import BaseCommand
from django.utils import timezone
from opal.models import Patient

from legacy.management.commands.flush_database import flush
from rbhl.episode_categories import OccupationalLungDiseaseEpisode
from rbhl.models import Demographics

sexLUT = {"F": "Female", "M": "Male", "U": "Not Known"}


def date_to_dob(s):
    """
    Convert a string representing a DoB into a timezone-aware Datetime object
    """
    if s == "":
        return None

    when = timezone.make_aware(datetime.strptime(s, "%d-%b-%y")).date()

    if when <= date.today():
        return when

    # Handle edge case of DoB being in the future
    return date(when.year - 100, when.month, when.day)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def handle(self, *args, **options):
        """
        Load the demographics from the database that talks to the PAS.
        Use these as our basis for matching against.
        """
        flush()

        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(options["file_name"], encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        # ignore rows with no DoB
        rows = filter(lambda r: r["Dateofbirth"] != "00-Jan-00", rows)

        demographics = []
        patients_imported = 0
        for row in rows:
            patient = Patient.objects.create()
            patient.create_episode(
                category_name=OccupationalLungDiseaseEpisode.display_name
            )

            demographics.append(
                Demographics(
                    hospital_number=row["Hospital Number"],
                    nhs_number=row["NHSnumber"].replace(" ", ""),
                    surname=row["Surname"],
                    first_name=row["Firstname"],
                    post_code=row["Postcode"],
                    sex=sexLUT.get(row["Sex"], None),
                    date_of_birth=date_to_dob(row["Dateofbirth"]),
                    patient=patient,
                )
            )

            patients_imported += 1

        Demographics.objects.bulk_create(demographics)

        print("Imported {} patients".format(patients_imported))
