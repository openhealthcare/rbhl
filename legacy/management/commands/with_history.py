"""
Management command to import all data to the database
"""
import csv
from datetime import date, datetime
import sys

from django.core.management import BaseCommand
from django.utils import timezone
from opal.models import Patient


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
        self.create_legacy(options["file_name"])
        self.convert_details()

    def create_legacy(self, file_name):
        """
        Load the demographics from the database that talks to the PAS.
        Use these as our basis for matching against.
        """
        # Open with utf-8-sig encoding to avoid having a BOM in the first
        # header string.
        with open(file_name, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        # ignore rows with no DoB
        rows = filter(lambda r: r["Dateofbirth"] != "00-Jan-00", rows)

        # ignore rows with no Hospital Number
        rows = filter(lambda r: r["Hospital Number"] != "", rows)

        patients_imported = 0
        for row in rows:
            # patient = Patient.objects.create()
            # patient.create_episode(
            #     category_name=OccupationalLungDiseaseEpisode.display_name
            # )
            # patient.demographics_set.get().update_from_dict(
            #     {
            #         "created": timezone.now(),
            #         "hospital_number": row["Hospital Number"],
            #         "nhs_number": row["NHSnumber"].replace(" ", ""),
            #         "surname": row["Surname"],
            #         "first_name": row["Firstname"],
            #         "post_code": row["Postcode"],
            #         "sex": sexLUT.get(row["Sex"], None),
            #         "date_of_birth": date_to_dob(row["Dateofbirth"]),
            #     },
            #     user=None,
            # )
            if Patient.objects.filter(
                demographics__hospital_number=row['Hospital Number']
            ).count() > 1:
                print(row)
                sys.exit()
            patient = Patient.objects.get(
                demographics__hospital_number=row["Hospital Number"]
            )

            patient.patientnumber_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "value": row["Patient_num"],
                },
                user=None
            )

            if any([row["GPname"], row["GPPostcode"]]):
                address = ", ".join(
                    [
                        row["GPAddress1"],
                        row["GPAddress2"],
                        row["GPAddress3"],
                        row["GPAddress4"],
                    ]
                )
                patient.gp_set.get().update_from_dict(
                    {
                        "created": timezone.now(),
                        "name": row["GPname"],
                        "address": address,
                        "post_code": row["GPPostcode"],
                    },
                    user=None
                )

            address = ", ".join(i for i in [
                row["ADDRESS1"],
                row["Address2"],
                row["Address3"],
                row["Address4"],
            ] if i)
            patient.address_set.get().update_from_dict(
                {
                    "created": timezone.now(),
                    "address": address,
                    "telephone": row["Telephone"],
                },
                user=None
            )

            patients_imported += 1

        print("Imported {} patients".format(patients_imported))

    def convert_details(self):
        patients = Patient.objects.all().prefetch_related(
            "contactdetails_set", "address_set"
        )
        for patient in patients:
            contact_details = patient.contactdetails_set.all()[0]
            address = patient.address_set.all()[0]
            changed = False
            if not contact_details.phone and address.telephone:
                contact_details.phone = address.telephone
                changed = True

            if not contact_details.address and address.address:
                contact_details.address = address.address
                changed = True

            if changed:
                contact_details.save()
