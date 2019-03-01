"""
Management command to import the actionlog csv from the admin database
"""
import csv

from django.core.management.base import BaseCommand
from opal.models import Patient

from rbhl.models import Letter
from rbhl.episode_categories import OccupationalLungDiseaseEpisode

from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError

from legacy.models import ActionLog
from legacy.utils import str_to_date, bol, inty


class Matcher(match.Matcher):
    direct_match_field     = match.Mapping(
        'Hospital Number', 'hospital_number'
    )

    attribute_match_fields = [
        match.Mapping('Patient Surname', 'surname'),
        match.Mapping('Patient First Name', 'first_name')
    ]
    demographics_fields    = [
        match.Mapping('Hospital Number', 'hospital_number'),
        match.Mapping('Patient Surname', 'surname'),
        match.Mapping('Patient First Name', 'first_name')
    ]


def create_unmatched_patient(row):
    row_demographcis_fields = {
        "Hospital Number": "hospital_number",
        "Patient First Name": "first_name",
        "Patient Surname": "surname"
    }
    patient = Patient.objects.create()
    patient.create_episode(
        category_name=OccupationalLungDiseaseEpisode.display_name
    )
    demographics = patient.demographics_set.get()

    for field, demographics_field in row_demographcis_fields.items():
        setattr(demographics, demographics_field, row[field])
    demographics.save()
    return patient


def create_clinic_log(row, episode):
    print('Creating ClinicLog')
    cliniclog = episode.cliniclog_set.get()

    cliniclog.seen_by           = row['SeenBy']
    cliniclog.clinic_date        = str_to_date(row['Clinicdate'])
    cliniclog.diagnosis_made    = bol(row['DiagnosisMade'])
    cliniclog.follow_up_planned = bol(row['FollowUp'])
    cliniclog.date_of_followup  = str_to_date(row['DateFollowUpAppt'])
    cliniclog.lung_function = bol(row['LungFunction'])
    cliniclog.lung_function_date = str_to_date(row['DateLungFunction'])
    cliniclog.lung_function_attendance = bol(row['Did patient attend LF?'])
    cliniclog.histamine = bol(row['Histamine'])
    cliniclog.histamine_date = str_to_date(row['DateHistamine'])
    cliniclog.histamine_attendance = bol(row['Did patient attend Histamine?'])
    cliniclog.peak_flow = bol(row['PeakFlow'])
    cliniclog.other_rbh_bloods = bol(row['BloodRBHlab'])
    cliniclog.immunology_oem = bol(row['ImmunologyOEM'])
    cliniclog.other_hostpital_info = bol(row['OtherHospitalInfo'])
    cliniclog.other_oh_info = bol(row['OherOHInfo'])
    cliniclog.other_gp_info = bol(row['OtherGPInfo'])
    cliniclog.work_samples = bol(row['Samples(Work)'])
    cliniclog.active = bol(row['Active'])
    cliniclog.save()


def create_contact_details(row, patient):
    print('Saving contact details')
    contact_details = patient.contactdetails_set.get()
    contact_details.mobile = row['Mobile']
    contact_details.phone = row['Telno']
    contact_details.email = row['Email']
    contact_details.save()


def create_referral(row, episode):
    print('Creating referral')
    referral = episode.referral_set.get()

    referral.referrer_title         = row['Referrerttl']
    referral.referrer_name          = row['Referrername']
    referral.date_of_referral       = str_to_date(row['DateReferral'])
    referral.date_referral_received = str_to_date(row['DateRecdReferral'])
    referral.date_first_contact     = str_to_date(row['DateFirstContact'])
    referral.comments               = row['Commentscontact']
    referral.date_first_appointment = str_to_date(row['DateFirstPatientAppt'])
    referral.attendance = bol(row['Did patient attend?'])
    referral.save()


def create_employment(row, episode):
    print('Creating Employment')
    employment = episode.employment_set.get()

    employment.employer    = row['Employer']
    employment.oh_provider = row['OH Provider']
    employment.firefighter = bol(row['Firefighter- pre-employment'])
    employment.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'file_name',
            help="Specify import file",
        )

    def handle(self, *args, **options):
        file_name = options.get("file_name")
        Letter.objects.all().delete()

        self.patients_imported = 0
        self.patients_missed = 0
        self.no_hosp_num = 0

        print('Open CSV to read')
        with open(file_name) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                print('Matching patient')
                if row['Hospital Number'] == '':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                try:
                    patient = matcher.direct_match()
                except PatientNotFoundError:
                    patient = create_unmatched_patient(row)
                except Exception:
                    print('uncaught')
                    print(row)
                    raise

                create_contact_details(row, patient)

                print('Fetching episode')
                episode = patient.episode_set.get()

                create_referral(row, episode)

                create_employment(row, episode)

                create_clinic_log(row, episode)

                print('Creating Letter')
                letter = Letter(episode=episode)
                letter.text = row['Comments1'].replace('\n', '\n\n')
                letter.save()

                print('Deleting any actionlogs')
                episode.actionlog_set.all().delete()

                print('Creating Action Log')
                actionlog = ActionLog(episode=episode)
                actionlog.general_notes = row['Other']
                actionlog.finaldays = inty(row['Finaldays'])

                actionlog.save()

                self.patients_imported += 1
                print('Imported Patient {0}'.format(
                    self.patients_imported,
                ))
                print(row)

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        return
