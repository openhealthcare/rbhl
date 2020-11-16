"""
Management command to import the blood book csv
"""
import csv
from time import time
from functools import wraps
from django.core.management import BaseCommand
from django.db import transaction
from legacy.utils import str_to_date
from legacy.models import BloodBook
from rbhl.models import Demographics


def timing(f):
    @wraps(f)
    def wrap(cmd, *args, **kw):
        ts = time()
        result = f(cmd, *args, **kw)
        te = time()
        cmd.stdout.write('timing_func: %r %2.4f sec' % (
            f.__name__, te-ts
        ))
        return result
    return wrap


def no_yes(field):
    field = field.strip().upper()
    if field == 'YES':
        return True
    if field == 'NO':
        return False
    return


def translate_ref_num(field):
    # IC OCC HEALTH is occationally typoed
    field = field.strip()
    if field == 'ICC.OCC.HLTH':
        return "IC.OCC.HLTH"
    if field == "ASTTRAZENECA":
        field = "ASTRAZENECA"
    return field


def get_precipitin(some_field):
    if some_field is None:
        return
    some_field = some_field.lower()
    lut = {
        "- ve": "-ve",
        "+ ve": "+ve",
        "weak +ve": "Weak +ve"
    }
    return lut.get(some_field, some_field)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    @timing
    @transaction.atomic
    def handle(self, *args, **options):
        file_name = options["file_name"]
        print('Opening {} to read'.format(file_name))
        with open(file_name) as f:
            rows = list(csv.DictReader(f))

        no_results = 0
        row_count = len(rows)
        no_patients = 0
        double_patients = 0
        self.bb_count = 0
        self.result_count = 0
        for row in rows:
            # if a row has no surname or any results skip it.
            if not row["SURNAME"].strip():
                no_patients += 1
                continue

            hospital_number = row["Hosp_no"].strip()
            first_name = row["FIRSTNAME"].strip()
            surname = row["SURNAME"].strip()
            date_of_birth = str_to_date(row["BIRTH"].strip())
            demographics = None

            if first_name and surname and date_of_birth:
                demographics = Demographics.objects.filter(
                    first_name__iexact=first_name,
                    surname__iexact=surname,
                    date_of_birth=date_of_birth
                )

            if not demographics:
                demographics = Demographics.objects.filter(
                    hospital_number=hospital_number
                )

            if not demographics:
                no_patients += 1
                continue

            if demographics.count() > 1:
                double_patients += 1
                continue

            patient = demographics.get().patient
            blood_book = self.create_blood_book_test(row, patient)
            if blood_book is None:
                no_results += 1
                continue
            self.create_blood_book_results_for_row(row, blood_book)

        self.stdout.write("Skipped {}/{} rows because no patient was found".format(
            no_patients, row_count
        ))
        self.stdout.write("Skipped {}/{} rows because duplicate patients found".format(
            double_patients, row_count
        ))
        self.stdout.write("{}/{} skipped due to no results".format(
            no_results, row_count
        ))
        self.stdout.write("{} created blood books".format(self.bb_count))
        self.stdout.write("{} created blood book results".format(self.result_count))

    def create_blood_book_test(self, row, patient):
        """
        Creates a Blood Book Test, 1 per row of the csv.
        """
        MAPPING = {
            "reference_number": lambda row: translate_ref_num(row["REFERENCE NO"]),
            "employer": "Employer",
            "oh_provider": "OH Provider",
            "blood_date": lambda row: str_to_date(row["BLOODDAT"]),
            "blood_number": "BLOODNO",
            "method": "METHOD",
            # Never filled in
            "blood_collected": "EDTA blood collected",
            # Filled in with poor data
            "date_dna_extracted": "Date DNA extracted",
            "information": "INFORMATION",
            "assayno": "ASSAYNO",
            "assay_date": lambda row: str_to_date(row["ASSAYDATE"]),
            "blood_taken": lambda row: str_to_date(row["BLOODTK"]),
            "blood_tm": "BLOODTM",
            "report_dt": lambda row: str_to_date(row["REPORTDT"]),
            "report_st": lambda row: str_to_date(row["REPORTST"]),
            "store": lambda row: no_yes(row["STORE"]),
            "exposure": "EXPOSURE",
            "antigen_type": "ANTIGENTYP",
            "comment": "Comment",
            "room": "Room",
            "batches": "Batches",
            "freezer": "Freezer",
            "shelf": "Shelf",
            "tray": "Tray",
            "vials": "Vials"
        }

        our_args = {}
        for i, v in MAPPING.items():
            if callable(v):
                our_args[i] = v(row)
            else:
                our_args[i] = row[v].strip()

        antigen_date = None
        try:
            antigen_date = str_to_date(row["ANTIGENDAT"])
        except ValueError:
            pass

        # antigen data is slightly garbled, lets strip out the obviously wrong.
        if antigen_date and antigen_date.year > 1969 and antigen_date.year < 2021:
            our_args["antigen_date"] = antigen_date

        # the csv has empty rows so just return if there are no values for that row
        if not any([i for i in our_args.values()]):
            return

        our_args["patient"] = patient
        self.bb_count += 1
        return BloodBook.objects.create(**our_args)

    def create_blood_book_results_for_row(self, row, blood_book):
        """
        Creates blood book results, a maximum of 11 per row of the csv.
        """
        mapping = {
            'RESULT': "result",
            'ALLERGEN': "allergen",
            'ANTIGENNO': "antigenno",
            'KUL': "kul",
            'CLASS': "klass",
            'RAST': "rast",
            'precipitin': "precipitin",
            'igg': "igg",
            'iggclass': "iggclass"
        }
        for i in range(1, 11):
            result_data = {}
            for csv_field, our_field in mapping.items():
                iterfield = '{}{}'.format(csv_field, i)
                value = row.get(iterfield, "")
                if value:
                    if csv_field == 'precipitin':
                        value = get_precipitin(value)
                    result_data[our_field] = value
            if any(result_data.values()):
                blood_book.bloodbookresult_set.create(**result_data)
                self.result_count += 1
