"""
Management command to bring in historic Peak Flow data
"""
import os
import csv
from django.core.management.base import BaseCommand
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError

from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('CRN', 'hospital_number')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'directory_name',
            help="Specify import directory",
        )

    def handle(self, *args, **kwargs):
        print('Deleting all existing Peak Flow objects')
        PeakFlowDay.objects.all().delete()
        PeakFlowIdentifier.objects.all().delete()

        dir_name = kwargs.get("directory_name")
        demographics_file_name = os.path.join(dir_name, "demographics.csv")
        flow_data_file_name = os.path.join(dir_name, "trial_day.csv")

        if not os.path.exists(demographics_file_name):
            raise ValueError(
                "We expect a demographics file called demographics.csv"
            )

        if not os.path.exists(flow_data_file_name):
            raise ValueError(
                "We expect a demographics file called trial_day.csv"
            )

        self.patients_imported = 0
        self.flow_days_imported = 0

        self.patients_missed = 0
        self.no_hosp_num = 0

        print('Import Peak Flow IDs')
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
                identifier.save()

        print('Imported {} matched Peak Flow Identifiers'.format(
            PeakFlowIdentifier.objects.all().count())
        )

        print('Import peak flow measurements')
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

                print('Creating Peak Flow Days')
                patient = patients[0].patient

                episode = patient.episode_set.get()

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

                day.day_num    = int(row["DAY_NUM"])
                day.trial_num  = int(row["TRIAL_NUM"])
                day.work_start = int(row["WORK_START"])
                day.work_end   = int(row["WORK_FINISH"])

                day.save()
                self.flow_days_imported += 1

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        print('Found {}'.format(PeakFlowIdentifier.objects.all().count()))
        print('With {} peak flow days'.format(self.flow_days_imported))
