"""
Management command to import the blood csv
"""
import csv
from time import time
from functools import wraps
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from legacy.utils import str_to_date
from plugins.lab.models import Bloods
from rbhl.models import Demographics, Employment, Referral
from opal.models import Patient

MARK_AS_NONE = set([
    "NOT APPLICABLE",
    "NOT KNOWN"
])


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
            un_filtered_rows = list(csv.DictReader(f))

        rows = []
        for row in un_filtered_rows:
            blood_date = str_to_date(row["BLOODDAT"])
            if not blood_date or blood_date.year < 2015:
                continue
            rows.append(row)

        no_results = 0
        row_count = len(rows)
        no_identifiers = 0
        patient_created = 0
        patient_matched = 0
        double_patients = 0
        self.bb_count = 0
        self.result_count = 0
        self.employment_created = 0
        self.employment_assigned = 0
        self.referral_created = 0
        self.referral_assigned = 0

        for row in rows:
            hospital_number = row["Hosp_no"].strip()
            first_name = row["FIRSTNAME"].strip()
            surname = row["SURNAME"].strip()
            date_of_birth = str_to_date(row["BIRTH"].strip())
            demographics = None
            blood_number = row["BLOODNO"].strip()

            # if we don't have firstname/surname/dob or hospital number
            # then we skip it
            if not first_name and not surname and not date_of_birth:
                if not hospital_number:
                    no_identifiers += 1
                    continue

            if first_name and surname and date_of_birth:
                demographics = Demographics.objects.filter(
                    first_name__iexact=first_name,
                    surname__iexact=surname,
                    date_of_birth=date_of_birth
                )
            if hospital_number:
                if demographics:
                    if demographics.exclude(hospital_number='').count() > 1:
                        demographics = demographics.filter(
                            hospital_number=hospital_number
                        )
                else:
                    demographics = Demographics.objects.filter(
                        hospital_number=hospital_number
                    )

            if not demographics and not hospital_number and blood_number:
                demographics_lookup = {}
                if first_name:
                    demographics_lookup["first_name__icontains"] = first_name
                if surname:
                    demographics_lookup["surname__icontains"] = surname
                if date_of_birth:
                    demographics_lookup["date_of_birth"] = date_of_birth
                demographics = Demographics.objects.filter(**demographics_lookup)
                patients = Patient.objects.filter(
                    bloods__blood_number=blood_number
                )
                demographics = demographics.filter(
                    patient_id__in=[i.id for i in patients]
                )

            if demographics and demographics.count() > 1:
                double_patients += 1
                continue

            if not demographics:
                patient = Patient.objects.create()
                patient.demographics_set.update(
                    first_name=first_name,
                    surname=surname,
                    date_of_birth=date_of_birth,
                    hospital_number=hospital_number
                )
                patient.episode_set.create()
                patient_created += 1
            else:
                patient = demographics.get().patient
                patient_matched += 1

            bloods = self.create_bloods_test(row, patient)
            if bloods is None:
                no_results += 1
                continue
            self.create_blood_results_for_row(row, bloods)

        self.stdout.write("Only looking at post 2015 rows {}/{}".format(
            len(rows), len(un_filtered_rows)
        ))

        self.stdout.write("Skipped {}/{} rows because no identifiers were found".format(
            no_identifiers, row_count
        ))

        self.stdout.write("Skipped {}/{} rows because duplicate patients found".format(
            double_patients, row_count
        ))
        self.stdout.write("{}/{} skipped due to no results".format(
            no_results, row_count
        ))
        self.stdout.write("Created {}/{} rows patients".format(
            patient_created, row_count
        ))
        self.stdout.write("Matched {}/{} rows patients".format(
            patient_matched, row_count
        ))
        self.stdout.write("{} employments created".format(
            self.employment_created
        ))
        self.stdout.write("{} existing employments assigned".format(
            self.employment_assigned
        ))
        self.stdout.write("{} existing referrals created".format(
            self.referral_created
        ))
        self.stdout.write("{} referrals assigned".format(
            self.referral_assigned
        ))
        self.stdout.write("{} created blood books".format(self.bb_count))
        self.stdout.write("{} created blood book results".format(self.result_count))

    def create_bloods_test(self, row, patient):
        """
        Creates a Bloods Test, 1 per row of the csv.
        """
        MAPPING = {
            # "reference_number": lambda row: translate_ref_num(row["REFERENCE NO"]),
            # "employer": "Employer",
            # "oh_provider": "OH Provider",
            "blood_date": lambda row: str_to_date(row["BLOODDAT"]),
            "blood_number": "BLOODNO",
            "method": "METHOD",
            # Never filled in
            "blood_collected": "EDTA blood collected",
            # Filled in with poor data
            "date_dna_extracted": "Date DNA extracted",
            # "information": "INFORMATION",
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

        bloods = Bloods.objects.create(patient=patient)
        for k, v in our_args.items():
            setattr(bloods, k, v)

        bloods.employment = self.get_or_create_employment_if_necessary(
            patient, row["Employer"], row["OH Provider"]
        )
        bloods.referral = self.get_or_create_referral_if_necessary(
            patient, row["Referrername"], str_to_date(row["BLOODDAT"])
        )
        bloods.save()

        self.bb_count += 1
        return bloods

    def get_or_create_referral_if_necessary(self, patient, referrer, blood_date):
        if not referrer or referrer.upper() in MARK_AS_NONE:
            return

        # if the referrer is OCCLD it is not an external referral
        # and we expect there to be a referrer with a different
        # name already existing. Otherwise just return None
        if referrer == "OCCLD":
            existing_referral = Referral.objects.filter(episode__patient=patient)
            if existing_referral:
                return existing_referral.first()
        qs = Referral.objects.filter(
            episode__patient=patient,
            referrer_name=referrer
        )
        current_referral = qs.first()
        if current_referral:
            self.referral_assigned += 1
            return current_referral
        episode = patient.episode_set.last()
        self.referral_created += 1
        return Referral.objects.create(
            created=timezone.now(),
            episode=episode,
            referrer_name=referrer,
            date_of_referral=blood_date,
            ocld=False
        )

    def get_or_create_employment_if_necessary(self, patient, employer, oh_provider):
        if employer and employer.upper() in MARK_AS_NONE:
            employer = None

        if oh_provider and oh_provider.upper() in MARK_AS_NONE:
            oh_provider = None

        if not employer and not oh_provider:
            return

        qs = Employment.objects.filter(episode__patient=patient)
        if employer :
            qs = qs.filter(employer=employer)
        if oh_provider:
            qs = qs.filter(oh_provider=oh_provider)
        current_employment = qs.first()
        if current_employment:
            self.employment_assigned += 1
            return current_employment
        episode = patient.episode_set.last()
        self.employment_created += 1
        return Employment.objects.create(
            created=timezone.now(),
            episode=episode,
            employer=employer,
            oh_provider=oh_provider
        )

    def create_blood_results_for_row(self, row, bloods):
        """
        Creates blood results, a maximum of 11 per row of the csv.
        """
        mapping = {
            'RESULT': "result",
            'ALLERGEN': "allergen",
            'ANTIGENNO': "phadia_test_code",
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
                    # one row is just a list of `
                    if isinstance(value, str) and not value.strip('`'):
                        continue
                    if csv_field == 'precipitin':
                        value = get_precipitin(value)
                    result_data[our_field] = value
            if any(result_data.values()):
                bloods.bloodresult_set.create(**result_data)
                self.result_count += 1
