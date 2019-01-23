"""
Management command to import all data to the database
"""
import csv
import datetime

from django.core.management import BaseCommand
from django.utils import timezone
import ffs

from plugins.trade.match import FieldConverter, Matcher, Mapping

from legacy.management.commands.flush_database import flush
from rbhl.episode_categories import OccupationalLungDiseaseEpisode

def sex_to_sex(raw_data, *args, **kwargs):
    raw = raw_data['Sex']
    if raw == 'M':
        return 'Male'
    if raw == 'F':
        return 'Female'
    if raw == 'U':
        return 'Not Known'
    if raw == '':
        return None
    raise ValueError('Unknown Sex: {}'.format(raw))


def date_to_dob(raw_data, *args, **kwargs):
    raw = raw_data['Dateofbirth']
    if raw == '':
        return None
    when = timezone.make_aware(
        datetime.datetime.strptime(raw, "%d-%b-%y")
    ).date()
    if when > datetime.date.today():
        when = datetime.date(when.year - 100, when.month, when.day)
    return when

def nhs_number_without_spaces(raw_data, *args, **kwargs):
    number = raw_data['NHSnumber']
    parts = number.split(' ')
    return ''.join(parts)


class PASMatcher(Matcher):
    direct_match_field = 'hospital_number'
    demographics_fields = [
        Mapping('Hospital Number', 'hospital_number'),
        FieldConverter(nhs_number_without_spaces, 'nhs_number'),
        Mapping('Surname', 'surname'),
        Mapping('Firstname', 'first_name'),
        Mapping('Postcode', 'post_code'),
        FieldConverter(sex_to_sex, 'sex' ),
        FieldConverter(date_to_dob, 'date_of_birth')
    ]


def load_PAS_demographics():
    """
    Load the demographics from the database that talks to the PAS.
    Use these as our basis for matching against.
    """
    data = ffs.Path('~/Documents/ohc/Brompton-17-Jan/patient details.csv')
    patients_imported = 0
    print('Beginning PAS DB demographics import ')
    with open(data.abspath) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Dateofbirth'] == '00-Jan-00':
                continue
            matcher = PASMatcher(row)
            patients_imported += 1
            patient = matcher.create()
            episode = patient.create_episode(
                category_name=OccupationalLungDiseaseEpisode.display_name
            )
            if patients_imported % 500 == 0:
                print(patients_imported)
    print('Imported {} patients'.format(patients_imported))


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        flush()
        load_PAS_demographics()
