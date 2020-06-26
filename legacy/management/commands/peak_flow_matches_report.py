"""
Management command to provide information about matches and misses
when importing historic peak flow data.
"""
import os
import csv

from django.core.management.base import BaseCommand
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError


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
        demographics_file_name = os.path.join(dir_name, "OCC_PATIENT.csv")

        self.patients_matched = 0
        self.patients_missed = 0
        self.no_hosp_num = 0

        self.missed_dicts = []

        print('Match Peak Flow IDs')
        with open(demographics_file_name) as f:
            reader = csv.DictReader(f)
            for row in reader:

                if row["CRN"] == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row)
                try:
                    matcher.direct_match()
                    self.patients_matched += 1
                except PatientNotFoundError:
                    self.patients_missed += 1
                    self.missed_dicts.append(row)
                    continue

        for row in self.missed_dicts:
            print(",".join(row.values()))
