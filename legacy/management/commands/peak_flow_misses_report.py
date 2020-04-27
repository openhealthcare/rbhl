"""
Management command to provide information about misses
when importing historic peak flow data.
"""
import os
import collections
import csv
import sys

from django.core.management.base import BaseCommand
from plugins.trade import match
from plugins.trade.exceptions import PatientNotFoundError

from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'directory_name',
            help="Specify import directory",
        )

    def handle(self, *args, **kwargs):

        month_counts = collections.defaultdict(int)

        dir_name = kwargs.get("directory_name")
#        demographics_file_name = os.path.join(dir_name, "OCC_PATIENT.csv" )
        demographics_file_name = 'peakflow.misses.csv'
        trial_file_name = os.path.join(dir_name, 'OCC_TRIAL.csv')

        with open(demographics_file_name) as f:
            reader = csv.reader(f)
            patients = [row for row in reader]
            occmednos = [p[0] for p in patients]

            with open(trial_file_name) as f2:
                reader = csv.DictReader(f2)
                for row in reader:
                    if row['OCCMEDNO'] in occmednos:
                        month_counts[row['START_DATE'][:7]] += 1

        for k, v in month_counts.items():
            print('{},{}'.format(k, v))
