"""
Management command to bring in historic Peak Flow data
"""
from django.core.management.base import BaseCommand
import ffs
from opal.core import exceptions, match

from rbhl.models import PeakFlowDay
from legacy.models import PeakFlowIdentifier


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('crn', 'hospital_number')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        print('Deleting all existing Peak Flow objects')
        PeakFlowDay.objects.all().delete()
        PeakFlowIdentifier.objects.all().delete()

        demographics_data = ffs.Path('~/Documents/RBHL/peakflow/demographics.csv')
        flow_data = ffs.Path('~/Documents/RBHL/peakflow/trial_day.csv')

        self.patients_imported = 0
        self.flow_days_imported = 0

        self.patients_missed = 0
        self.no_hosp_num = 0

        print('Import Peak Flow IDs')
        with demographics_data.csv(header=True) as csv:
            for row in csv:
                if row.crn == 'NULL':
                    self.no_hosp_num += 1
                    continue

                matcher = Matcher(row._asdict())
                try:
                    patient = matcher.direct_match()
                except exceptions.PatientNotFoundError:
                    self.patients_missed += 1
                    continue

                print('Creating Peak Flow Identifier')

                identifier = PeakFlowIdentifier(patient=patient)
                identifier.occmendo = int(row.occmedno)
                identifier.save()

        print('Imported {} matched Peak Flow Identifiers'.format(PeakFlowIdentifier.objects.all().count()))

        print('Import peak flow measurements')
        with flow_data.csv(header=True) as csv:
            for row in csv:

                patients = PeakFlowIdentifier.objects.filter(occmendo=int(row.occmedno))
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
                data = row.trial_data.split(',')[:-1]

                flow_fields = [
                    'flow_0000', 'flow_0100', 'flow_0200', 'flow_0300', 'flow_0400', 'flow_0500',
                    'flow_0600', 'flow_0700', 'flow_0800', 'flow_0900', 'flow_1000', 'flow_1100',
                    'flow_1200', 'flow_1300', 'flow_1400', 'flow_1500', 'flow_1600', 'flow_1700',
                    'flow_1800', 'flow_1900', 'flow_2000', 'flow_2100', 'flow_2200', 'flow_2300',
                ]

                for i, field in enumerate(flow_fields):
                    setattr(day, field, data[i])

                day.day_num    = int(row.day_num)
                day.trial_num  = int(row.trial_num)
                day.work_start = int(row.work_start)
                day.work_end   = int(row.work_finish)

                day.save()
                self.flow_days_imported += 1

        print('Missed {}'.format(self.patients_missed))
        print('Skipped {} (no hosp num)'.format(self.no_hosp_num))
        print('Found {}'.format(PeakFlowIdentifier.objects.all().count()))
        print('With {} peak flow days'.format(self.flow_days_imported))
