"""
Management command to bring in historic Peak Flow data
"""
import os
import csv
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction, Max
from plugins.trade import match
import datetime


from opal.models import Patient
from rbhl.models import PeakFlowDay, ImportedFromPreviousDatabase
from legacy.models import PeakFlowIdentifier


DEMOGRAPHICS_FILE = "OCC_PATIENT.CSV"
TRIAL_DAY = "OCC_TRIAL_DAY.CSV"
TRIAL_START_DAY = "OCC_TRIAL.CSV"
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
        with open(file_name, mode="r", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                occmedno = int(row["OCCMEDNO"])
                trial_num = int(row["TRIAL_NUM"])
                key = (occmedno, trial_num)

                # these patients have duplicate trials
                # lets ignore them for the time being
                if occmedno in (104, 280, 289,):
                    result[key] = DELETED
                    continue

                # this patient has a start date of null
                # so lets mark it as deleted and not
                # add it
                if occmedno == 34:
                    result[key] = DELETED
                    continue

                if row["START_DATE"] == "NULL":
                    raise ValueError("start date is null for {}".format(key))

                start_dt = datetime.datetime.strptime(
                    row["START_DATE"], "%Y-%m-%d %H:%M:%S.000"
                )

                start = start_dt.date()

                existing_result = result.get(key)

                # if there are multiple occmedno/trial id and they are
                # different we should error
                if existing_result and not existing_result == start:
                    raise ValueError(
                        "Duplicate row found in {}".format(file_name)
                    )

                if int(row["TRIAL_DELETED"]):
                    start = DELETED

                if key in result and not result[key] == start:
                    raise ValueError(
                        "Inconsistent start date found for {}".format(key)
                    )

                # ignore deleted rows
                if int(row["TRIAL_DELETED"]):
                    result[key] = DELETED
                else:
                    result[key] = start
        return result

    def raise_trial_numbers(self, peak_flow_days):
        """
        Trial number is a 1 indexed numeric sequence starting
        with the oldest peak flow day.

        The peak flow days that we are importing are all older than
        the peak flows that currently exist.

        Bump the existing trial numbers so that they are above
        the ones that we are importing.

        We could do this in a more database efficient way
        but given its only a few and a one off import
        this is hopefully clearer.
        """
        episode_id_to_trial_num = defaultdict(int)

        for peak_flow_day in peak_flow_days:
            trial_num = peak_flow_day.trial_num
            if episode_id_to_trial_num[peak_flow_day.episode_id] < trial_num:
                episode_id_to_trial_num[peak_flow_day.episode_id] = trial_num

        for episode_id, trial_num in episode_id_to_trial_num.items():
            max_trial_num = PeakFlowDay.objects.filter(
                episode_id=episode_id
            ).aggregate(max_trial_num=Max('trial_num'))
            if max_trial_num["max_trial_num"]:
                existing_peak_flows = PeakFlowDay.objects.filter(
                    episode_id=episode_id
                )
                for existing_peak_flow in existing_peak_flows:
                    new_trial_num = existing_peak_flow.trial_num + trial_num
                    existing_peak_flow.trial_num = new_trial_num
                    existing_peak_flow.save()

    @transaction.atomic
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

        # deleting all patients that have information
        # imported from the peak flow database but
        # no clinic logs beside them.
        created_patients = Patient.objects.filter(
            episode__importedfrompreviousdatabase__isnull=False
        )
        created_patients = created_patients.filter(
            episode__cliniclog=None
        )
        print('Delete {} patients created by the importer'.format(
            created_patients.count())
        )
        created_patients.delete()

        imported_records = ImportedFromPreviousDatabase.objects.all()
        imported_records = imported_records.select_related('episode')

        print('Delete all imported records created by the importer')
        for imported in imported_records:
            imported.epsiode.peakflowday_set.filter(
                trial_num=imported.trial_num
            ).delete()

        print('Delete all peak flow identifiers')
        PeakFlowIdentifier.objects.all().delete()

        self.patients_imported = 0
        self.flow_days_imported = 0

        self.patients_missed = 0
        self.no_hosp_num = 0

        peak_flow_idenitifiers = []

        with open(demographics_file_name, mode="r", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["CRN"] == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                patient, created = matcher.match_or_create()
                demographics = patient.demographics()

                if created:
                    first_name, surname = row["PAT_NAME"].rsplit(" ", 1)
                    demographics.first_name = first_name
                    demographics.surname = surname
                    demographics.save()
                    patient.create_episode()

                print("Updating demographics")
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
                age = int(row["AGE"])
                if not age:
                    age = None

                identifier = PeakFlowIdentifier(
                    patient=patient, age=age
                )
                identifier.occmendo = int(row["OCCMEDNO"])
                peak_flow_idenitifiers.append(identifier)

        PeakFlowIdentifier.objects.bulk_create(peak_flow_idenitifiers)

        print('Imported {} matched Peak Flow Identifiers'.format(
            PeakFlowIdentifier.objects.all().count())
        )

        peak_flow_days = []

        print('Import peak flow measurements')

        # for a given occmedno/day num/trial num
        # if there are multiple rows in the csv
        # and those rows are different we should error
        expected_unique = {}
        with open(flow_data_file_name, mode="r", encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                identifier = PeakFlowIdentifier.objects.filter(
                    occmendo=int(row["OCCMEDNO"])
                )
                if identifier.count() > 1:
                    print(row)
                    raise ValueError('Too many identifiers')
                if identifier.count() == 0:
                    print('Missed identifier - skipping')
                    continue

                trial_num = int(row["TRIAL_NUM"])
                occmedno = int(row["OCCMEDNO"])
                day_num = int(row["DAY_NUM"])
                # we don't expect duplicates of occmedno, trial_num, day_num
                key = (occmedno, trial_num, day_num,)
                if key in expected_unique:
                    if expected_unique[key] == row["TRIAL_DATA"]:
                        continue
                    raise ValueError('Duplicate trial day found')

                start_date = occ_med_no_and_trial_num_to_start_date[
                    (occmedno, trial_num,)
                ]

                if start_date == DELETED:
                    print('{} has been deleted, skipping'.format(key))
                    continue

                expected_unique[key] = row["TRIAL_DATA"]

                patient = identifier[0].patient

                episode = patient.episode_set.get()

                if not patient.demographics().date_of_birth:
                    age = identifier[0].age
                    ImportedFromPreviousDatabase.objects.get_or_create(
                        episode=episode,
                        trial_number=trial_num,
                        age=age
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
            self.raise_trial_numbers(peak_flow_days)
            PeakFlowDay.objects.bulk_create(peak_flow_days)

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        print('Found {}'.format(PeakFlowIdentifier.objects.all().count()))
        print('With {} peak flow days'.format(self.flow_days_imported))
