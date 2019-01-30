"""
Management command to import the actionlog csv from the admin database
"""
import datetime
import csv

from django.core.management.base import BaseCommand
from django.utils import timezone
import ffs
from opal.core import exceptions
from opal.models import Patient, Episode

from rbhl.models import Demographics, ContactDetails, Referral, Employment, ClinicLog, Letter

from plugins.trade import match
from plugins.trade.match import FieldConverter, Matcher, Mapping
from plugins.trade.exceptions import PatientNotFoundError

from legacy.models import ActionLog
from legacy.episode_categories import AdminDatabase
from legacy.utils import str_to_date, bol, inty

class Matcher(match.Matcher):
    direct_match_field     = match.Mapping('Hospital Number', 'hospital_number')

    attribute_match_fields = [
        match.Mapping('Patient Surname',    'surname'),
        match.Mapping('Patient First Name', 'first_name')
    ]
    demographics_fields    = [
        Mapping('Hospital Number', 'hospital_number'),
        match.Mapping('Patient Surname',    'surname'),
        match.Mapping('Patient First Name', 'first_name')
    ]


class Command(BaseCommand):

    def handle(self, *args, **options):
        Letter.objects.all().delete()

        data = ffs.Path('~/Documents/ohc/Brompton-17-Jan/action.log.csv')
        self.patients_imported = 0
        self.patients_missed = 0
        self.no_hosp_num = 0

        print('Open CSV to read')
        with open(data.abspath) as csvfile:
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
                    self.patients_missed += 1
                    continue
                except:
                    print('uncaught')
                    print(row)
                    raise


                print('Saving contact details')
                contact_details = patient.contactdetails_set.get()
                contact_details.mobile = row['Mobile']
                contact_details.phone = row['Telno']
                contact_details.email = row['Email']
                contact_details.save()

                print('Fetching episode')
                episode = patient.episode_set.get()

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
                referral.firefighter = bol(row['Firefighter- pre-employment'])
                referral.save()

                print('Creating Employment')
                employment = episode.employment_set.get()

                employment.employer    = row['Employer']
                employment.oh_provider = row['OH Provider']
                employment.save()

                print('Creating ClinicLog')
                cliniclog = episode.cliniclog_set.get()

                cliniclog.seen_by           = row['SeenBy']
                cliniclog.clinicdate        = str_to_date(row['Clinicdate'])
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
