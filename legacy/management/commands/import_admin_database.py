"""
Management command to import the actionlog csv from the admin database
"""
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
import ffs
from opal.core import match, exceptions
from opal.models import Patient, Episode

from rbhl.models import Demographics, ContactDetails, Referral, Employment, ClinicLog, Letter

from legacy.models import ActionLog
from legacy.episode_categories import AdminDatabase
from legacy.utils import str_to_date, bol, inty


class Matcher(match.Matcher):
    direct_match_field     = 'hospital_number'
    attribute_match_fields = [
        match.Mapping('patient_surname',    'surname'),
        match.Mapping('patient_first_name', 'first_name')
    ]
    demographics_fields    = [
        'hospital_number',
        match.Mapping('patient_surname',    'surname'),
        match.Mapping('patient_first_name', 'first_name')
    ]


class Command(BaseCommand):

    def handle(self, *args, **options):
        Letter.objects.all().delete()

        data = ffs.Path('~/Documents/RBHL/admindb/actionlog.csv')
        self.patients_imported = 0
        self.patients_missed = 0
        self.no_hosp_num = 0

        print('Open CSV to read')
        with data.csv(header=True) as csv:

            for row in csv:
                print('Matching patient')
                if row.hospital_number == '':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row._asdict())
                try:
                    patient = matcher.direct_match()
                except exceptions.PatientNotFoundError:
                    self.patients_missed += 1
                    continue
                except:
                    print('uncaught')
                    print(row._asdict())
                    raise


                print('Saving contact details')
                contact_details = patient.contactdetails_set.get()
                contact_details.mobile = row.mobile
                contact_details.phone = row.telno
                contact_details.email = row.email
                contact_details.save()

                print('Fetching episode')
                episode = patient.episode_set.get()

                print('Creating referral')
                referral = episode.referral_set.get()

                referral.referrer_title         = row.referrerttl
                referral.referrer_name          = row.referrername
                referral.date_of_referral       = str_to_date(row.datereferral)
                referral.date_refferal_received = str_to_date(row.daterecdreferral)
                referral.date_first_contact     = str_to_date(row.datefirstcontact)
                referral.comments               = row.commentscontact
                referral.save()

                print('Creating Employment')
                employment = episode.employment_set.get()

                employment.employer    = row.employer
                employment.oh_provider = row.oh_provider
                employment.save()

                print('Creating ClinicLog')
                cliniclog = episode.cliniclog_set.get()

                cliniclog.seen_by           = row.seenby
                cliniclog.clinicdate        = str_to_date(row.clinicdate)
                cliniclog.diagnosis_made    = bol(row.diagnosismade)
                cliniclog.follow_up_planned = bol(row.followup)
                cliniclog.date_of_followup  = str_to_date(row.datefollowupappt)
                cliniclog.save()

                print('Creting Letter')
                letter = Letter(episode=episode)
                letter.text = row.comments1.replace('\n', '\n\n')
                letter.save()

                print('Deleting any actionlogs')
                episode.actionlog_set.all().delete()

                print('Creating Action Log')
                actionlog = ActionLog(episode=episode)
                actionlog.datefirst_appointment = str_to_date(row.datefirstpatientappt)
                actionlog.attendance = bol(row.did_patient_attend)
                actionlog.peak_flow = bol(row.peakflow)
                actionlog.immunology_oem = bol(row.immunologyoem)
                actionlog.histamine = bol(row.histamine)
                actionlog.histamine_date = str_to_date(row.datehistamine)
                actionlog.histamine_attendance = bol(row.did_patient_attend_histamine)
                actionlog.lung_function = bol(row.lungfunction)
                actionlog.lung_function_date = str_to_date(row.datelungfunction)
                actionlog.lung_function_attendance = bol(row.did_patient_attend_lf)
                actionlog.work_samples = bol(row.sampleswork)
                actionlog.other_hostpital_info = bol(row.otherhospitalinfo)
                actionlog.other_oh_info = bol(row.oherohinfo)
                actionlog.other_gp_info = bol(row.othergpinfo)
                actionlog.other_rbh_bloods = bol(row.bloodrbhlab)
                actionlog.firefighter = bol(row.firefighter_preemployment)
                actionlog.active = bol(row.active)
                actionlog.general_notes = row.other
                actionlog.finaldays = inty(row.finaldays)

                actionlog.save()

                self.patients_imported += 1
                print('Imported Patient {0}'.format(
                    self.patients_imported,
                ))
                print(row)

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        return
