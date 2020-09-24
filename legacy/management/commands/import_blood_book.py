"""
Management command to import the blood book csv
"""
import csv
import datetime
from time import time
from functools import wraps
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rbhl.episode_categories import OccupationalLungDiseaseEpisode
from legacy.utils import str_to_date
from legacy.models import BloodBookPatient, BloodBookEpisode
from opal.models import Patient, Episode
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


def str_to_time(s):
    if s == '':
        return
    when = timezone.make_aware(
        datetime.datetime.strptime(s, "%m/%d/%y %H:%M:%S")
    ).time()
    return when


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


def contains_numbers(some_str):
    """
    Returns true if the string contains any numbers
    """
    return any(i for i in some_str if i.isnumeric())


def get_longest(*strs):
    """
    Returns the longest of a list of strings
    """
    strs = [i for i in strs if i]
    if strs:
        return sorted(strs, key=lambda x: len(x), reverse=True)[0]
    return None


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


def get_or_create_blood_book_patient(row):
    """
    A blood book patient is a unique hospital number,
    first_name, surname, dob as appears in the csv.
    Due to typos etc an rbhl patient can have 1+ blood book patients.

    Hospital number is unreliable and will give false positives.
    First name, surname and dob is unreliable as first name is often
    but not always given as an initial however it should not give false
    negatives.

    At the moment we will just do first name, surname, dob but should
    change this to more sophisticated matching later.
    """
    hospital_number = row["Hosp_no"].strip()
    dob = str_to_date(
        row['BIRTH'], no_future_dates=True
    )
    first_name = row["FIRSTNAME"].strip()
    surname = row["SURNAME"].strip()
    return BloodBookPatient.objects.get_or_create(
        first_name=first_name,
        surname=surname,
        date_of_birth=dob,
        hospital_number=hospital_number
    )


def get_or_create_blood_book_episode(bb_patient, row):
    """
    A blood book episode is a unique blood date/referrer name
    oh provider and employer set.

    We consider an episode to be a referral.
    We therefore expect a maximum of one referral for a blood sample date.
    """
    blood_date = str_to_date(row["BLOODDAT"])
    referrer_name = row["Referrername"].strip()
    oh_provider = row["OH Provider"].strip()
    employer = row["Employer"].strip()
    exposures = row["EXPOSURE"].strip()

    return bb_patient.bloodbookepisode_set.get_or_create(
        blood_date=blood_date,
        referrer_name=referrer_name,
        oh_provider=oh_provider,
        employer=employer,
        exposures=exposures
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def handle(self, *args, **options):
        file_name = options["file_name"]
        print('Open CSV to read')
        with open(file_name) as f:
            rows = list(csv.DictReader(f))

        cleaned_rows = []
        for row in rows:
            # if a row has no surname or any results skip it.
            if not row["SURNAME"].strip():
                continue
            blood_book_results = self.get_result_details(row)
            if not len(blood_book_results):
                continue
            cleaned_rows.append(row)

        self.stdout.write(
            self.style.SUCCESS("Rows skipped".format(len(rows), len(cleaned_rows)))
        )
        self.create_blood_book_patients_and_episodes(cleaned_rows)
        self.create_rbhl_patients()
        self.create_rbhl_episodes()
        self.create_blood_book_test_models(cleaned_rows)

    @timing
    @transaction.atomic
    def create_blood_book_patients_and_episodes(self, rows):
        """
        Saves distinct patient data and distinct episode/referral data.
        These can then be collapsed down at a later date.
        """
        self.stdout.write("Creating blood book patient and episodes")
        patient_count = 0
        episode_count = 0
        for row in rows:
            # Surname is our most reliable identifier, if its not populated
            # skip the row
            bb_patient, bb_patient_created = get_or_create_blood_book_patient(row)
            bb_episode, bb_episode_created = get_or_create_blood_book_episode(
                bb_patient, row
            )
            if bb_patient_created:
                patient_count += 1
            if bb_episode_created:
                episode_count += 1
        msg = "Created blood book patients: {}, Created blood book episodes: {}".format(
            patient_count, episode_count
        )
        self.stdout.write(self.style.SUCCESS(msg))

    @timing
    @transaction.atomic
    def create_rbhl_patients(self):
        """
        HN can be unreliable so we cannot use it as a single identifier.

        So we do 3 matching theories.

        1. first_name, surname, dob
        2. hn, dob
        3. hn, surname
        4. if no hn or dob, map to first_name and surname

        When creating a patient for a hosptial number we use the longest unique
        bb patient hospital number that contains a numeric digit
        """
        self.stdout.write("Creating rbhl patients")
        patient_details = BloodBookPatient.objects.all().values(
            "hospital_number", "first_name", "surname", "date_of_birth"
        ).distinct()
        patients_created = 0
        patients_found = 0

        disinct_patinet_details = set([tuple(i.values()) for i in patient_details])
        if not len(patient_details) == len(disinct_patinet_details):
            raise ValueError("Distinct does not work like you think it does...")

        for patient_detail in patient_details:
            hn = patient_detail["hospital_number"].strip()
            dob = patient_detail["date_of_birth"]
            surname = patient_detail["surname"].strip()
            first_name = patient_detail["first_name"].strip()
            patient = Patient.objects.filter(
                demographics__first_name__iexact=first_name,
                demographics__surname__iexact=surname,
                demographics__date_of_birth=dob
            ).first()
            if not patient and hn and dob:
                patient = Patient.objects.filter(
                    demographics__hospital_number=hn,
                    demographics__date_of_birth=dob
                ).first()

            if not patient and hn and dob:
                patient = Patient.objects.filter(
                    demographics__hospital_number=hn,
                    demographics__surname__iexact=surname
                ).first()

            if patient:
                patients_found += 1

            if not patient:
                rows = BloodBookPatient.objects.filter(**patient_detail)
                hns = list(set([row.hospital_number for row in rows]))
                hns = [i for i in hns if i and contains_numbers(i)]
                hns = sorted(hns, key=lambda x: len(x), reverse=True)
                hn_to_use = ""

                for hn in hns:
                    if BloodBookPatient.objects.exclude(**patient_detail).filter(
                        hospital_number=hn
                    ).exists():
                        continue

                    hn_to_use = hn
                    break
                patient = Patient.objects.create()
                patient.demographics_set.update(
                    first_name=patient_detail["first_name"],
                    surname=patient_detail["surname"],
                    date_of_birth=patient_detail["date_of_birth"],
                    hospital_number=hn_to_use
                )
                patients_created += 1
            BloodBookPatient.objects.filter(
                **patient_detail
            ).update(
                patient=patient
            )
        msg = "Created patients: {}, Already existing patients: {}"
        self.stdout.write(
            self.style.SUCCESS(msg.format(patients_created, patients_found))
        )
        qs = Patient.objects.annotate(
            count=Count('bloodbookpatient')
        ).filter(count__gt=1)
        msg = "Single patients with multiple rows: {}".format(qs.count())
        self.stdout.write(self.style.SUCCESS(msg))

    @timing
    @transaction.atomic
    def create_rbhl_episodes(self):
        """
        We consider a blood book referral to be a unique patient/blood date.

        If there exists an episode within a year of the blood date, we will use
        that episode.

        If there are multiple bb episodes with patient/blood date we will use the
        referral details employer details that are the longest.

        If these have not been populated in existing episodes then we shall use these
        """
        self.stdout.write("Creating rbhl episodes")
        episodes_created = 0
        episodes_found = 0
        referrals_updated = 0
        employment_updated = 0
        episode_details = BloodBookEpisode.objects.all().values(
            "blood_book_patient_id", "blood_date"
        ).distinct()
        disinct_episode_details = set([tuple(i.values()) for i in episode_details])
        if not len(episode_details) == len(disinct_episode_details):
            raise ValueError("Distinct does not work like you think it does...")
        episode_details = sorted(
            episode_details,
            key=lambda x: x["blood_date"] or datetime.datetime.max.date()
        )
        for episode_detail in episode_details:
            patient = Patient.objects.get(
                bloodbookpatient__id=episode_detail["blood_book_patient_id"]
            )
            episodes = patient.episode_set.all()

            # If we have no blood date, use any episode
            if not episode_detail["blood_date"]:
                if not episodes:
                    episode = patient.episode_set.create()
                    episodes_created += 1
            else:
                # Get the episode that is within a year of the blood date.
                # The existing system does not have duplicate episodes.
                # but the blood book does.
                earliest = episode_detail["blood_date"] - datetime.timedelta(
                    365
                )
                latest = episode_detail["blood_date"] + datetime.timedelta(
                    365
                )
                episode = patient.episode_set.filter(
                    referral__date_of_referral__gt=earliest
                ).filter(
                    referral__date_of_referral__lt=latest
                ).first()

                if episode:
                    episodes_found += 1
                else:
                    # If an episode does not exist create it.
                    episode = patient.episode_set.create(
                        category_name=OccupationalLungDiseaseEpisode.display_name
                    )
                    episodes_created += 1

            bb_episodes = BloodBookEpisode.objects.filter(
                **episode_detail
            )
            bb_episodes.update(episode=episode)
            referrer_name = get_longest(*[i.referrer_name for i in bb_episodes])
            oh_provider = get_longest(*[i.oh_provider for i in bb_episodes])
            employer = get_longest(*[i.employer for i in bb_episodes])

            referral = episode.referral_set.get()
            if not referral.referrer_name:
                referral.referrer_name = referrer_name
                referrals_updated += 1
                referral.save()

            employment = episode.employment_set.get()
            employment_changed = False
            if not employment.employer and employer:
                employment.employer = employer
                employment_changed = True
            if not employment.oh_provider and oh_provider:
                employment.oh_provider = oh_provider
                employment_changed = True
            if not employment.exposures:
                exposures = set(
                    i.exposures.strip() for i in bb_episodes if i.exposures.strip()
                )
                if exposures:
                    employment.exposures = "\n".join(sorted(list(exposures)))
                employment_changed = True

            if employment_changed:
                employment_updated += 1
                employment.save()
        msg = "Created episodes: {}, Already existing episodes: {}"
        self.stdout.write(
            self.style.SUCCESS(msg.format(episodes_created, episodes_found))
        )
        msg = "Referrals updated: {}, Employment updated: {}"
        self.stdout.write(
            self.style.SUCCESS(msg.format(referrals_updated, employment_updated))
        )

        qs = Episode.objects.annotate(
            count=Count('bloodbookepisode')
        ).filter(count__gt=1)
        msg = "Single episodes with multiple rows: {}".format(qs.count())
        self.stdout.write(self.style.SUCCESS(msg))

    def get_or_create_blood_book_test(self, row):
        """
        A blood book test is a
        unique
        method, assay_number, assay_date, blood_number, sample_received, report_date,
        report_submitted, reference_number, store, antigen_type
        as appears in the csv
        """
        hospital_number = row["Hosp_no"].strip()
        dob = str_to_date(
            row['BIRTH'], no_future_dates=True
        )
        first_name = row["FIRSTNAME"].strip()
        surname = row["SURNAME"].strip()

        patient = BloodBookPatient.objects.get(
            hospital_number=hospital_number,
            date_of_birth=dob,
            first_name=first_name,
            surname=surname
        ).patient

        # unique fields
        MAPPING = {
            "method": "METHOD",
            "assay_number": "ASSAYNO",
            "assay_date": lambda row: str_to_date(row["ASSAYDATE"]),
            "blood_number": "BLOODNO",
            "sample_received": lambda row: str_to_date(row["BLOODDAT"]),
            "report_date": lambda row: str_to_date(row["REPORTDT"]),
            "report_submitted": lambda row: str_to_date(row["REPORTST"]),
            "reference_number": lambda row: translate_ref_num(row["REFERENCE NO"]),
            "store": lambda row: no_yes(row["STORE"]),
            "antigen_type": "ANTIGENTYP",
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

        blood_taken_date = str_to_date(row["BLOODTK"])

        if blood_taken_date:
            blood_taken_time = str_to_time(row["BLOODTM"])
            if not blood_taken_time:
                blood_taken_time = datetime.datetime.min.time()
            our_args["blood_taken"] = timezone.make_aware(datetime.datetime.combine(
                blood_taken_date, blood_taken_time
            ))

        blood_book = None
        for bb in patient.bloodbook_set.all():
            matched = True
            for k, our_val in our_args.items():
                their_val = getattr(bb, k)
                if their_val and our_val and not their_val == our_val:
                    matched = False
            if matched:
                blood_book = bb
                break
        if blood_book:
            for k, our_val in our_args.items():
                if getattr(blood_book, k) is None and our_val:
                    setattr(blood_book, k, our_val)
            blood_book.save()
            created = False
        else:
            blood_book = patient.bloodbook_set.create()
            for k, our_val in our_args.items():
                setattr(blood_book, k, our_val)
            blood_book.save()
            created = True
            return blood_book, True

        information = blood_book.information
        if row["Comment"]:
            information = "{}\n{}".format(information, row["Comment"])
        for k in ["Room", "Freezer", "Shelf", "Vials", "Batches"]:
            if row[k]:
                information = "{}\n{}: {}".format(
                    information, k, row[k]
                )
        if information:
            blood_book.information = information.strip()
            blood_book.save()
        return blood_book, created

    def get_result_details(self, row):
        """
        Return a list of the data that will be stored as results.
        """
        mapping = {
            'RESULT': "result",
            'ALLERGEN': "allergen",
            'ANTIGENNO': "antigen_number",
            'KUL': "kul",
            'CLASS': "ige_class",
            'RAST': "rast",
            'precipitin': "precipitin",
            'igg': "igg_mg",
            'iggclass': "igg_class"
        }
        result = []
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
                result.append(result_data)
        return result

    @timing
    @transaction.atomic
    def create_blood_book_test_models(self, rows):
        blood_books_created = 0
        results_created = 0
        for row in rows:
            blood_book_test, bb_created = self.get_or_create_blood_book_test(row)
            if bb_created:
                blood_books_created += 1
            results = self.get_result_details(row)
            for result_data in results:
                blood_book_result = blood_book_test.bloodbookresult_set.create()
                for k, v in result_data.items():
                    setattr(blood_book_result, k, v)
                blood_book_result.save()
                results_created += 1
        msg = "Blood books created {}. results created: {}".format(
            blood_books_created, results_created
        )
        self.stdout.write(self.style.SUCCESS(msg))
