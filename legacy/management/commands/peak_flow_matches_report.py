"""
Management command to provide information about matches and misses
when importing historic peak flow data.
"""
import os
import csv
import sys

from django.core.management.base import BaseCommand
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError

from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('CRN', 'hospital_number__iexact')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'directory_name',
            help="Specify import directory",
        )

    def handle(self, *args, **kwargs):

        dir_name = kwargs.get("directory_name")
        demographics_file_name = os.path.join(dir_name, "OCC_PATIENT.csv" )

        self.patients_matched = 0
        self.patients_missed = 0
        self.no_hosp_num = 0

        self.missed_dicts = []

#        print('Match Peak Flow IDs')
        with open(demographics_file_name) as f:
            reader = csv.DictReader(f)
            for row in reader:

                if row["CRN"] == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                try:
                    patient = matcher.direct_match()
                    self.patients_matched += 1
                except PatientNotFoundError:
                    self.patients_missed += 1
                    self.missed_dicts.append(row)
                    continue

        numbes_below_500 = 0
        for row in self.missed_dicts:
            print(",".join(row.values()))

            #if int(row['\ufeffOCCMEDNO']) <= 500:
            #     numbes_below_500 += 1

            # else:
            #     print('{} {}'.format(row['CRN'], row['PAT_NAME']))

        # print('Matched {}'.format(self.patients_matched))
        # print('Missed {}'.format(self.patients_missed))
        # print('Below 500 {}'.format(numbes_below_500))
        # print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
