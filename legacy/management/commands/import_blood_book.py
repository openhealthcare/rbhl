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
from plugins.lab.models import Observation, LabTest, Specimen


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


def get_or_create_specimen(patient, row):
    existing_specimen = patient.specimen_set.filter(
        exposure__iexact=row["EXPOSURE"],
        blood_date=str_to_date(row["BLOODDAT"]),
    ).first()

    if existing_specimen:
        return existing_specimen, False

    store = None
    if row["STORE"] == 'YES':
        store = True
    elif row["STORE"] == "NO":
        store = False

    vials = None
    if row["Vials"]:
        vials = row["Vials"]
        # fixes a typo
        vials = vials.replace("..", ".")

    return patient.specimen_set.create(
        exposure=row["EXPOSURE"],
        reference_number=row['REFERENCE NO'],
        blood_date=str_to_date(row["BLOODDAT"]),
        blood_taken=str_to_date(row["BLOODTK"]),
        information=row["INFORMATION"],
        assay_no=row["ASSAYNO"],
        assay_date=str_to_date(row["ASSAYDATE"]),
        report_dt=str_to_date(row["REPORTDT"]),
        report_st=str_to_date(row["REPORTST"]),
        store=store,
        antigen_type=row["ANTIGENTYP"],
        comment=row["Comment"],
        vials=vials
    ), True


def create_lab_test(specimen, data_row):
    csv_field_to_observation_name = {
        'RESULT': Observation.RESULT,
        'ALLERGEN': Observation.ALLERGEN,
        'ANTIGENNO': Observation.ANTIGEN_NO,
        'KUL': Observation.KUL,
        'CLASS': Observation.CLASS,
        'RAST': Observation.RAST,
        'precipitin': Observation.PRECIPITIN,
        'igg': Observation.IGG
    }

    for i in range(1, 11):
        lab_test = LabTest(
            specimen=specimen,
            test_name=LabTest.BLOOD_BOOK
        )
        update_values = {}
        for csv_field, observation_name in csv_field_to_observation_name.items():
            iterfield = '{}{}'.format(csv_field, str(i))
            value = data_row.get(iterfield, "")
            if value:
                update_values[observation_name] = value

        if any(update_values.values()):
            for obs_name, obs_value in update_values.items():
                lab_test.save()
                lab_test.observation_set.create(
                    observation_name=obs_name,
                    observation_value=obs_value
                )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @transaction.atomic
    def handle(self, *args, **options):
        patients_imported = 0

        print('Open CSV to read')
        with open(options["file_name"]) as f:
            reader = csv.DictReader(f)
            duplicates = []
            referrals = []
            books = []
            results = []

            for data in reader:
                hospital_number = data["Hosp_no"].strip()
                demographics = None
                dob = str_to_date(
                    data['BIRTH'], no_future_dates=True
                )

                if hospital_number:
                    try:
                        demographics = get_demographics(
                            hospital_number=data["Hosp_no"].strip()
                        )
                        if demographics and not demographics.date_of_birth:
                            demographics.date_of_birth = dob
                            demographics.save()
                    except ValueError:
                        # If we have a patient with a duplicate
                        # hospital number try a lookup with name/dob
                        pass

                if not demographics:
                    try:
                        demographics = get_demographics(
                            first_name__iexact=data["FIRSTNAME"].strip(),
                            surname__iexact=data["SURNAME"].strip(),
                            date_of_birth=dob
                        )
                    except ValueError:
                        duplicates.append(data)
                        continue

                if demographics:
                    patient = demographics.patient
                else:
                    patient = Patient.objects.create()
                    patient.demographics_set.update(
                        hospital_number=data["Hosp_no"],
                        first_name=data["FIRSTNAME"],
                        surname=data["SURNAME"],
                        date_of_birth=dob
                    )
                    patients_imported += 1

                data['BIRTH'] = str_to_date(
                    data['BIRTH'], no_future_dates=True
                )

                episode = patient.create_episode(
                    category_name=episode_categories.BloodBook.display_name
                )

                referral = episode.referral_set.get()
                referral.referrer_name = data["Referrername"]
                referral.referrer_title = data["Referrerttl"]
                referral.save()
                referrals.append(referral)

                specimen, _ = get_or_create_specimen(patient, data)
                create_lab_test(specimen, data)

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

        # although they are actually updated they singletons
        # therefore essentially created
        msg = "Created {} referrals".format(len(referrals))
        self.stdout.write(self.style.SUCCESS(msg))

        BloodBook.objects.bulk_create(books)
        msg = "Created {} legacy blood books".format(len(books))
        self.stdout.write(self.style.SUCCESS(msg))

        BloodBookResult.objects.bulk_create(results)
        msg = "Created {} legacy blood results".format(len(results))
        self.stdout.write(self.style.SUCCESS(msg))

        msg = "Skipping {} duplicates".format(len(duplicates))
        self.stdout.write(self.style.WARNING(msg))

        msg = "Created {} specimens".format(Specimen.objects.all().count())
        self.stdout.write(self.style.SUCCESS(msg))
        msg = "Created {} lab tests".format(LabTest.objects.all().count())
        self.stdout.write(self.style.SUCCESS(msg))
        msg = "Created {} observations".format(Observation.objects.all().count())
        self.stdout.write(self.style.SUCCESS(msg))

        msg = "Impored {} patients".format(
            patients_imported
        )
        self.stdout.write(self.style.SUCCESS(msg))
