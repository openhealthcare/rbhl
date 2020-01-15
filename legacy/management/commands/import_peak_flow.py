"""
Management command to bring in historic Peak Flow data
"""
import os
import csv
import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError

from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier, OccTrial, OccTrialDay
from opal.models import Patient


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('CRN', 'hospital_number')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'directory_name',
            help="Specify import directory",
        )

    def import_demographics_file(self, demographics_file_name):
        print('Import Peak Flow IDs')
        PeakFlowIdentifier.objects.all().delete()
        with open(demographics_file_name, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader()
            for row in reader:
                pfi = PeakFlowIdentifier()

                if not row["CRN"] == 'NULL':
                    pfi.hospital_number = row["CRN"]

                row["occmedno"] = int(row["OCCMEDNO"])

                row_height = int(row["HEIGHT"])

                if not row_height == 0:
                    pfi.height = row_height

                if row["SEX"] == "M":
                    pfi.sex = pfi.MALE
                elif row["SEX"] == "F":
                    pfi.sex = pfi.FEMALE

                row_employ = row["COMPANY_NAME"].strip()

                if not row_employ == "0":
                    pfi.company = row_employ

                pfi.name = row["PAT_NAME"]



                if row["CRN"] == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                try:
                    patient = matcher.direct_match()
                except PatientNotFoundError:
                    self.patients_missed += 1
                    continue

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

                identifier = PeakFlowIdentifier(patient=patient)
                identifier.occmedno = int(row["OCCMEDNO"])
                identifier.save()

                # at the moment no patients have more than one episode
                episode = patient.episode_set.get()
                employment = episode.employment_set.get()

                row_employ = row["COMPANY_NAME"].strip()

                if row_employ == "0":
                    row_employ = None

                # If the don't already have an employer but there is one in the
                # file then use that
                if row_employ and not employment.employer:
                    employment.employer = row_employ
                    employment.save()

            print('Imported {} matched Peak Flow Identifiers'.format(
                PeakFlowIdentifier.objects.all().count())
            )

    def import_occ_trial_file(self, occ_trial_file_name):
        print(f'Import OCC Trial {occ_trial_file_name}')
        OccTrial.objects.all().delete()
        with open(occ_trial_file_name, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                model_args = {
                    k.lower(): int(v) for k, v in row.items()
                    if not k == "TrialID" and not k == "START_DATE"
                }
                model_args["trial_id"] = row["TrialID"]
                if row["START_DATE"].strip() == "NULL":
                    self.no_start_date += 1
                    continue

                if "-" in row["START_DATE"]:
                    model_args["start_date"] = datetime.datetime.strptime(
                        row["START_DATE"][:10], '%Y-%m-%d'
                    ).date()
                else:
                    model_args["start_date"] = datetime.datetime.strptime(
                        row["START_DATE"][:10], '%d/%m/%Y'
                    ).date()

                model_args['trial_deleted'] = bool(int(model_args['trial_deleted']))

                if OccTrial.objects.filter(
                    occmedno=model_args["occmedno"],
                    trial_num=model_args["trial_num"],
                    trial_id=model_args["trial_id"],
                    trial_deleted=model_args["trial_deleted"],
                ).exists():
                    if OccTrial.objects.filter(**model_args).exists():
                        self.duplicate_trial_row += 1
                        continue
                    else:
                        self.duplicate_trial_row_with_different_values += 1
                        continue

                OccTrial.objects.create(**model_args)

    def import_occ_trial_day_file(self, occ_trial_day_file_name):
        print(f'Import OCC Trial Day {occ_trial_day_file_name}')
        OccTrialDay.objects.all().delete()
        with open(occ_trial_day_file_name, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                model_args = {
                    k.lower(): int(v) for k, v in row.items() if not k == "TRIAL_DATA"
                }
                model_args['published'] = bool(model_args['published'])
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
                    model_args[field] = int(float(data[i].rstrip('.')))

                if OccTrialDay.objects.filter(
                    occmedno=model_args["occmedno"],
                    trial_num=model_args["trial_num"],
                    day_num=model_args["day_num"],
                    published=model_args["published"],
                ).exists():
                    if OccTrialDay.objects.filter(**model_args).exists():
                        self.duplicate_trial_day_row += 1
                        continue
                    else:
                        v = OccTrialDay.objects.filter(
                            occmedno=model_args["occmedno"],
                            trial_num=model_args["trial_num"],
                            day_num=model_args["day_num"],
                            published=model_args["published"],
                        ).get()
                        self.duplicate_trial_day_row_with_different_values += 1
                        continue

                OccTrialDay.objects.create(**model_args)

    def import_data(self, dir_name):
        demographics_file_name = os.path.join(dir_name, "OCC_PATIENT.CSV")
        trial_day_file_name = os.path.join(dir_name, "OCC_TRIAL_DAY.CSV")
        trial_file_name = os.path.join(dir_name, "OCC_TRIAL.CSV")

        if not os.path.exists(demographics_file_name):
            raise ValueError(
                f"We expect a demographics file called {demographics_file_name}"
            )

        if not os.path.exists(trial_day_file_name):
            raise ValueError(
                f"We expect a demographics file called {trial_day_file_name}"
            )

        if not os.path.exists(trial_file_name):
            raise ValueError(
                f"We expect a demographics file called {trial_file_name}"
            )

        # demographics checks
        self.patients_missed = 0
        self.no_hosp_num = 0

        # trial checks
        self.no_start_date = 0
        self.duplicate_trial_row = 0
        self.duplicate_trial_row_with_different_values = 0

        # trial day checks
        self.duplicate_trial_day_row = 0
        self.duplicate_trial_day_row_with_different_values = 0

        self.import_demographics_file(demographics_file_name)
        self.import_occ_trial_file(trial_file_name)
        self.import_occ_trial_day_file(trial_day_file_name)

        print("=== Demographics ===")
        print(f'Missed {self.patients_missed}')
        print(f'No hospital number {self.no_hosp_num}')
        print(f'Total skipped {self.patients_missed + self.no_hosp_num}')
        print(f'Identifiers added {PeakFlowIdentifier.objects.all().count()}')

        occ_trials = OccTrial.objects.filter(trial_deleted=False).exclude(
            patient=None
        )
        occ_trial_days = OccTrialDay.objects.filter(published=True).exclude(
            patient=None
        )

        print("=== Trials ===")
        print(f"No start date {self.no_start_date}")
        print(f"Duplicate trial rows {self.duplicate_trial_row}")
        print(f"Duplicate trial rows with different values {self.duplicate_trial_row_with_different_values}")
        print(f"Total skipped {self.no_start_date + self.duplicate_trial_row_with_different_values}")
        print(f"Trials added {occ_trials.count()}")

        print("=== Trial days ===")
        print(f"Duplicate rows with the same values {self.duplicate_trial_day_row}")
        print(f"Duplicate rows with the different values {self.duplicate_trial_day_row_with_different_values}")
        print(f"Total skipped {self.duplicate_trial_day_row_with_different_values}")
        print(f"Total added {occ_trial_days.count()}")

    def process_trial_days(self):
        created = 0
        patients = Patient.objects.exclude(peakflowidentifier=None)
        patients = patients.exclude(episode__peakflowday=None)

        # we know this patient has a peak flow entry and will handle manually
        patients = patients.exclude(id=32333)

        if patients:
            print(patients.get().demographics().name)
            raise ValueError(
                'We already have peak flow days loaded for these patients'
            )

        # for the patient that has a new peak flow, we'll bump their trial num
        # by one
        to_update = PeakFlowDay.objects.filter(episode__patient_id=32333)
        for i in to_update:
            i.trial_num += 1
            i.save()

        occ_trials = OccTrial.objects.filter(trial_deleted=False).exclude(
            patient=None
        )
        occ_trial_days = OccTrialDay.objects.exclude(
            patient=None
        )

        for trial in occ_trials:
            days = occ_trial_days.filter(
                patient=trial.patient, trial_num=trial.trial_num
            )
            for day in days:
                model_args = {
                    "episode": trial.patient.episode_set.get(),
                    "date": trial.start_date + datetime.timedelta(day.day_num),
                    "treatment_taken": day.drug,
                    "work_day": day.is_work_day
                }
                fields = [
                    "flow_0000",
                    "flow_0100",
                    "flow_0200",
                    "flow_0300",
                    "flow_0400",
                    "flow_0500",
                    "flow_0600",
                    "flow_0700",
                    "flow_0800",
                    "flow_0900",
                    "flow_1000",
                    "flow_1100",
                    "flow_1200",
                    "flow_1300",
                    "flow_1400",
                    "flow_1500",
                    "flow_1600",
                    "flow_1700",
                    "flow_1800",
                    "flow_1900",
                    "flow_2000",
                    "flow_2100",
                    "flow_2200",
                    "flow_2300",
                    "trial_num",
                    "day_num"
                ]
                for field in fields:
                    model_args[field] = getattr(day, field)

                PeakFlowDay.objects.get_or_create(
                    **model_args
                )

                created += 1

        print(f"Added {created}")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        dir_name = kwargs.get("directory_name")
        self.import_data(dir_name)
        self.process_trial_days()
