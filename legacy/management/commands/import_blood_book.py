"""
Management command to import the blood book csv
"""
from django.core.management import BaseCommand
import ffs

from opal.core import match

from legacy import episode_categories
from legacy.utils import str_to_date
from legacy.models import Referral, BloodBook, BloodBookResult


class Matcher(match.Matcher):
    direct_match_field = match.Mapping('hosp_no', 'hospital_number')
    attribute_match_fields = [
        match.Mapping('firstname', 'first_name'),
        'surname',
        match.Mapping('birth', 'date_of_birth')
    ]
    demographics_fields = [
        match.Mapping('firstname', 'first_name'),
        'surname',
        match.Mapping('birth', 'date_of_birth'),
        match.Mapping('hosp_no', 'hospital_number')
    ]


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = ffs.Path('~/Documents/RBHL/bloods/bloodbook.csv')
        self.patients_imported = 0

        print('Open CSV to read')
        with data.csv(header=True) as csv:

            for row in csv:
                print('Matching patient')

                data = row._asdict()

                data['birth'] = str_to_date(data['birth'], no_future_dates=True)

                matcher = Matcher(data)
                # print(matcher.get_demographic_dict())
                # import sys;sys.exit()
                patient, created = matcher.match_or_create()

                if not created:
                    demographics = patient.demographics_set.get()
                    demographics.date_of_birth = data['birth']
                    demographics.save()

                print('Creating episdoe')
                episode = patient.create_episode(
                    category_name=episode_categories.BloodBook.display_name
                )

                print('Creating referral')
                referral = Referral(episode=episode)
                referral.referrer_name = row.referrername
                referral.referrer_title = row.referrerttl
                referral.save()

                print('Creating blood book entry')
                book = BloodBook(episode=episode)
                book.reference_number = row.reference_no
                book.blood_date = str_to_date(row.blooddat)
                book.blood_number = row.bloodno
                book.method = row.method
                book.blood_collected = row.edta_blood_collected
                book.date_dna_extracted = row.date_dna_extracted
                book.information = row.information
                book.assayno = row.assayno
                book.assay_date = str_to_date(row.assaydate)
                book.blood_taken = str_to_date(row.bloodtk)
                book.blood_tm = str_to_date(row.bloodtm)
                book.report_dt = str_to_date(row.reportdt)
                book.report_st = str_to_date(row.reportst)
                book.employer = row.employer
                book.store = row.store
                book.exposure = row.exposure
                try:
                    book.antigen_date = str_to_date(row.antigendat)
                except ValueError:
                    # We know that sometimes the data claims that the value of this field
                    # should be month number -1098.
                    #
                    # Strptime will complain that -1098 is not a month in the format %m.
                    # This seems eminently reasonable. Allow it to complain, but move on.
                    pass
                book.antigen_type = row.antigentyp
                book.comment = row.comment
                book.oh_provider = row.oh_provider
                book.batches = row.batches
                book.room = row.room
                book.freezer = row.freezer
                book.shelf = row.shelf
                book.tray = row.tray
                book.vials = row.vials
                book.save()

                print('Creating Blood results')

                fieldnames = [
                    'result', 'allergen', 'antigenno', 'kul',
                    'class', 'rast', 'precipitin', 'igg', 'iggclass'
                ]

                for i in range(1, 11):
                    result_data = {}
                    for field in fieldnames:
                        iterfield = '{}{}'.format(field, str(i))
                        value = getattr(row, iterfield, "")
                        if value:
                            if field == 'class':
                                field = 'klass'
                            result_data[field] = value

                    if any(result_data.values()):
                        result_data['episode'] = episode
                        result = BloodBookResult(**result_data)
                        result.save()
                self.patients_imported += 1
                print('{} ({})'.format(patient.demographics_set.get().name, self.patients_imported))
