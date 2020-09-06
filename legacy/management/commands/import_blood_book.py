"""
Management command to import the blood book csv
"""
import csv
from django.core.management import BaseCommand
from django.db import transaction

from legacy import episode_categories
from legacy.utils import str_to_date
from legacy.models import BloodBook, BloodBookResult
from opal.models import Patient
from rbhl.models import Demographics


def create_blood_book(row, episode):
    book = BloodBook(episode=episode)
    book.reference_number = row['REFERENCE NO']
    book.blood_date = str_to_date(row["BLOODDAT"])
    book.blood_number = row["BLOODNO"]
    book.method = row["METHOD"]
    book.blood_collected = row['EDTA blood collected']
    book.date_dna_extracted = row["Date DNA extracted"]
    book.information = row["INFORMATION"]
    book.assayno = row["ASSAYNO"]
    book.assay_date = str_to_date(row["ASSAYDATE"])
    book.blood_taken = str_to_date(row["BLOODTK"])
    book.blood_tm = str_to_date(row["BLOODTM"])
    book.report_dt = str_to_date(row["REPORTDT"])
    book.report_st = str_to_date(row["REPORTST"])
    book.employer = row["Employer"]
    book.store = row["STORE"]
    book.exposure = row["EXPOSURE"]
    try:
        book.antigen_date = str_to_date(row["ANTIGENDAT"])
    except ValueError:
        # We know that sometimes the data claims that the value of this field
        # should be month number -1098.
        #
        # Strptime will complain that -1098 is not a month in the format %m.
        # This seems eminently reasonable. Allow it to complain, but move on.
        pass
    book.antigen_type = row["ANTIGENTYP"]
    book.comment = row["Comment"]
    book.oh_provider = row["OH Provider"]
    book.batches = row["Batches"]
    book.room = row["Room"]
    book.freezer = row["Freezer"]
    book.shelf = row["Shelf"]
    book.tray = row["Tray"]
    book.vials = row["Vials"]
    book.referrer_name = row["Referrername"]
    book.referrer_title = row["Referrerttl"]
    return book


def get_demographics(**demographics_kwargs):
    demographics = Demographics.objects.filter(
        **demographics_kwargs
    )
    if len(demographics) == 1:
        return demographics[0]
    elif len(demographics) > 1:
        msg = "Duplicate patient for {}".format(
            demographics_kwargs
        )
        print(msg)
        raise ValueError(msg)
    return None


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def handle(self, *args, **options):
        file_name = options["file_name"]
        self.create_legacy_models(file_name)

    @transaction.atomic
    def create_legacy_models(self, file_name):
        patients_imported = 0

        print('Open CSV to read')
        with open(file_name) as f:
            reader = csv.DictReader(f)
            duplicates = []
            books = []
            results = []

            for data in reader:
                hospital_number = data["Hosp_no"].strip()
                demographics = None
                dob = str_to_date(
                    data['BIRTH'], no_future_dates=True
                )
                first_name = data["FIRSTNAME"].strip()
                surname = data["SURNAME"].strip()
                blood_book_ref_number = data['REFERENCE NO'].strip()
                # if its an empty string, lets save it as None
                if not blood_book_ref_number:
                    blood_book_ref_number = None

                if hospital_number:
                    try:
                        demographics = get_demographics(
                            hospital_number=data["Hosp_no"].strip()
                        )
                    except ValueError:
                        # If we have a patient with a duplicate
                        # hospital number try a lookup with name/dob
                        pass

                if not demographics and blood_book_ref_number:
                    # Note although blood_book_reference_number is never populated
                    # outside this file, some patients have multiple episodes
                    # so when that's the case make sure we don't create multiple
                    # patients.
                    # The exception catching is temporary as we need to look at the
                    # reference numbers
                    try:
                        demographics = get_demographics(
                            blood_book_ref_number=blood_book_ref_number
                        )
                    except ValueError:
                        pass

                if not demographics:
                    try:
                        demographics = get_demographics(
                            first_name__iexact=first_name,
                            surname__iexact=surname,
                            date_of_birth=dob
                        )
                    except ValueError:
                        duplicates.append(data)
                        continue

                if demographics:
                    if not demographics.date_of_birth:
                        demographics.date_of_birth = dob
                    if not demographics.surname:
                        demographics.surname = surname
                    if not demographics.first_name:
                        demographics.first_name = first_name
                    if not demographics.blood_book_ref_number and blood_book_ref_number:
                        demographics.blood_book_ref_number = blood_book_ref_number
                    demographics.save()
                    patient = demographics.patient
                else:
                    patient = Patient.objects.create()
                    patient.demographics_set.update(
                        hospital_number=hospital_number,
                        first_name=first_name,
                        surname=surname,
                        date_of_birth=dob,
                        blood_book_ref_number=blood_book_ref_number
                    )
                    patients_imported += 1

                episode = patient.create_episode(
                    category_name=episode_categories.BloodBook.display_name
                )

                books.append(create_blood_book(data, episode))

                fieldnames = [
                    'RESULT', 'ALLERGEN', 'ANTIGENNO', 'KUL',
                    'CLASS', 'RAST', 'precipitin', 'igg', 'iggclass'
                ]

                for i in range(1, 11):
                    result_data = {}
                    for field in fieldnames:
                        iterfield = '{}{}'.format(field, str(i))
                        value = data.get(iterfield, "")
                        if value:
                            if field == 'CLASS':
                                field = 'klass'
                            field = field.lower()
                            result_data[field] = value

                    if any(result_data.values()):
                        result_data['episode'] = episode
                        result = BloodBookResult(**result_data)
                        results.append(result)

        BloodBook.objects.bulk_create(books)
        msg = "Created {} legacy blood books".format(len(books))
        self.stdout.write(self.style.SUCCESS(msg))

        BloodBookResult.objects.bulk_create(results)
        msg = "Created {} legacy blood results".format(len(results))
        self.stdout.write(self.style.SUCCESS(msg))

        msg = "Skipping {} duplicates".format(len(duplicates))
        self.stdout.write(self.style.WARNING(msg))

        msg = "Impored {} patients".format(
            patients_imported
        )
        self.stdout.write(self.style.SUCCESS(msg))
