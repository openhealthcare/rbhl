"""
Management command to bring in historic Peak Flow data
"""
import os
import csv
from django.core.management.base import BaseCommand
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError
import datetime


from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier


DEMOGRAPHICS_FILE = "demographics.csv"
TRIAL_DAY = "trial_day.csv"
TRIAL_START_DAY = "OCC_TRIAL.csv"
DELETED = "DELETED"


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('CRN', 'hospital_number')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'directory_name',
            help="Specify import directory",
        )

    def get_start_date_map(self, dir_name):
        result = {}
        file_name = os.path.join(dir_name, TRIAL_START_DAY)
        with open(file_name) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["START_DATE"] == "NULL":
                    continue

                start_dt = datetime.datetime.strptime(
                    row["START_DATE"], "%Y-%m-%d %H:%M:%S.000"
                )

                start = start_dt.date()
                occmedno = int(row["OCCMEDNO"])
                trial_num = int(row["TRIAL_NUM"])

                # these patients have duplicate trials but
                # don't match any existing patients
                if occmedno in (104, 280):
                    continue
                key = (occmedno, trial_num)

                existing_result = result.get(key)
                if existing_result and not existing_result == start:
                    raise ValueError(
                        "Duplicate row found in {}".format(file_name)
                    )

                # ignore deleted rows
                if int(row["TRIAL_DELETED"]):
                    result[key] = DELETED
                else:
                    result[key] = start
        return result

    def handle(self, *args, **kwargs):
        dir_name = kwargs.get("directory_name")
        demographics_file_name = os.path.join(dir_name, DEMOGRAPHICS_FILE)
        flow_data_file_name = os.path.join(dir_name, TRIAL_DAY)

        for file_name in [DEMOGRAPHICS_FILE, TRIAL_DAY, TRIAL_START_DAY]:
            if not os.path.exists(os.path.join(dir_name, file_name)):
                raise ValueError(
                    "We expect a file called {}".format(file_name)
                )

        occ_med_no_and_trial_num_to_start_date = self.get_start_date_map(
            dir_name
        )

        print('Deleting non user created Peak Flow objects')
        PeakFlowDay.objects.filter(created_by=None).delete()
        PeakFlowIdentifier.objects.all().delete()

        self.patients_imported = 0
        self.flow_days_imported = 0

        self.patients_missed = 0
        self.no_hosp_num = 0

        peak_flow_idenitifiers = []

        with open(demographics_file_name) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["CRN"] == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                try:
                    patient = matcher.direct_match()
                except PatientNotFoundError:
                    self.patients_missed += 1
                    continue

                print("Updating demographics")
                demographics = patient.demographics()
                demographics_changed = False

                if row["HEIGHT"] and int(row["HEIGHT"]):
                    demographics.height = int(row["HEIGHT"])
                    demographics_changed = True

                if row["SEX"] and not demographics.sex:
                    if row["SEX"] == "M":
                        demographics_changed = True
                        demographics.sex = "Male"
                    elif row["SEX"] == "F":
                        demographics_changed = True
                        demographics.sex = "Female"
                if demographics_changed:
                    demographics.save()

                print('Creating Peak Flow Identifier')
                identifier = PeakFlowIdentifier(patient=patient)
                identifier.occmendo = int(row["OCCMEDNO"])
                peak_flow_idenitifiers.append(identifier)

        PeakFlowIdentifier.objects.bulk_create(peak_flow_idenitifiers)

        print('Imported {} matched Peak Flow Identifiers'.format(
            PeakFlowIdentifier.objects.all().count())
        )

        peak_flow_days = []

        print('Import peak flow measurements')
        expected_unique = set()
        with open(flow_data_file_name) as f:
            reader = csv.DictReader(f)

            for row in reader:
                patients = PeakFlowIdentifier.objects.filter(
                    occmendo=int(row["OCCMEDNO"])
                )
                if patients.count() > 1:
                    print(row)
                    raise ValueError('Too many identifiers')
                if patients.count() == 0:
                    print('Missed identifier - skipping')
                    continue

                trial_num = int(row["TRIAL_NUM"])
                occmedno = int(row["OCCMEDNO"])
                day_num = int(row["DAY_NUM"])
                # we don't expect duplicates of occmedno, trial_num, day_num
                key = (occmedno, trial_num, day_num,)
                if key in expected_unique:
                    raise ValueError('Duplicate trial day found')
                expected_unique.add(key)

                patient = patients[0].patient

                episode = patient.episode_set.get()

                if episode.peakflowday_set.exists():
                    raise ValueError(
                        'Manually entered peak flow exists for this patient'
                    )

                print('Creating Peak Flow Days')
                day = PeakFlowDay(episode=episode)
                data = row["TRIAL_DATA"].split(',')[:-1]

                flow_fields = [
                    'flow_0000', 'flow_0100', 'flow_0200',
                    'flow_0300', 'flow_0400', 'flow_0500',
                    'flow_0600', 'flow_0700', 'flow_0800',
                    'flow_0900', 'flow_1000', 'flow_1100',
                    'flow_1200', 'flow_1300', 'flow_1400',
                    'flow_1500', 'flow_1600', 'flow_1700',
                    'flow_1800', 'flow_1900', 'flow_2000',
                    'flow_2100', 'flow_2200', 'flow_2300',
                ]

                start_date = occ_med_no_and_trial_num_to_start_date[
                    (occmedno, trial_num,)
                ]

                if start_date == DELETED:
                    print('{} has been deleted, skipping'.format(key))
                    continue

                for i, field in enumerate(flow_fields):
                    setattr(day, field, data[i])

                day.day_num    = day_num
                day.date = start_date + datetime.timedelta(day.day_num - 1)
                day.trial_num  = int(row["TRIAL_NUM"])
                work_start = bool(int(row["WORK_START"]))
                work_end = bool(int(row["WORK_FINISH"]))
                day.work_day = work_start or work_end
                peak_flow_days.append(day)
                self.flow_days_imported += 1
            PeakFlowDay.objects.bulk_create(peak_flow_days)

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        print('Found {}'.format(PeakFlowIdentifier.objects.all().count()))
        print('With {} peak flow days'.format(self.flow_days_imported))
