"""
Management command to import the blood book csv
"""
import csv
import datetime
from time import time
from functools import wraps
from django.core.management import BaseCommand
from django.db import transaction

from rbhl.episode_categories import OccupationalLungDiseaseEpisode
from legacy.utils import str_to_date
from legacy.models import BloodBookPatient, BloodBookEpisode
from opal.models import Patient
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
    We consider an episode to be a referral.
    We therefore expect a maximum of one referral for a blood sample date.
    """
    blood_date = str_to_date(row["BLOODDAT"])
    referrer_name = row["Referrername"].strip()
    oh_provider = row["OH Provider"].strip()
    employer = row["Employer"].strip()

    return bb_patient.bloodbookepisode_set.get_or_create(
        blood_date=blood_date,
        referrer_name=referrer_name,
        oh_provider=oh_provider,
        employer=employer
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", help="Specify import file")

    def handle(self, *args, **options):
        file_name = options["file_name"]
        print('Open CSV to read')
        with open(file_name) as f:
            rows = [list(csv.DictReader(f))[0]]

        self.create_blood_book_patients_and_episodes(rows)
        self.create_rbhl_patients()
        self.create_rbhl_episodes()

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
        skipped = 0
        for row in rows:
            # Surname is our most reliable identifier, if its not populated
            # skip the row
            if not row["SURNAME"].strip():
                skipped += 1
                continue
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
        msg = "{}. Skipped patients: {}".format(msg, skipped)
        self.stdout.write(self.style.SUCCESS(msg))

    @timing
    @transaction.atomic
    def create_rbhl_patients(self):
        """
        For the moment we get or create based on first_name, surname, dob
        We can do better than this, but this should always be correct.

        When creating a patient for a hosptial number we use the longest unique
        bb patient hospital number that contains a numeric digit
        """
        self.stdout.write("Creating rbhl patients")
        patient_details = BloodBookPatient.objects.all().values(
            "first_name", "surname", "date_of_birth"
        ).distinct()
        patients_created = 0
        patients_found = 0

        disinct_patinet_details = set([tuple(i.values()) for i in patient_details])
        if not len(patient_details) == len(disinct_patinet_details):
            raise ValueError("Distinct does not work like you think it does...")

        for patient_detail in patient_details:
            patient = Patient.objects.filter(
                demographics__first_name__iexact=patient_detail["first_name"],
                demographics__surname__iexact=patient_detail["surname"],
                demographics__date_of_birth=patient_detail["date_of_birth"]
            ).first()
            if patient:
                patients_found += 1
            else:
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
                    episodes_found += 1

            bb_episodes = BloodBookEpisode.objects.filter(
                **episode_detail
            )
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
