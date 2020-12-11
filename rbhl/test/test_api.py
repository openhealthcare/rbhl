"""
Unittests for rbhl.api
"""
import datetime
from rest_framework.reverse import reverse
from opal.core.test import OpalTestCase
from rbhl import api
from rbhl.api import PeakFlowGraphData


class GetRangesTestCase(OpalTestCase):
    def test_get_empty_array(self):
        self.assertEqual([], api.get_ranges([]))

    def test_get_one_number(self):
        self.assertEqual([{'start': 1, 'end': 1}], api.get_ranges([1]))

    def test_get_two_single_number_ranges(self):
        expected = [
            {'start': 1, 'end': 1},
            {'start': 3, 'end': 3}
        ]
        self.assertEqual(expected, api.get_ranges([1, 3]))

    def test_get_range(self):
        self.assertEqual([{'start': 1, 'end': 3}], api.get_ranges([1, 2, 3]))
        self.assertEqual(
            [{'start': 1, 'end': 5}], api.get_ranges([1, 2, 3, 4, 5])
        )
        self.assertEqual(
            [{'start': 1, 'end': 9}],
            api.get_ranges([1, 2, 3, 4, 5, 6, 7, 8, 9])
        )

    def test_get_single_and_range(self):
        expected = [
            {'start': 1, 'end': 1},
            {'start': 3, 'end': 6}
        ]
        self.assertEqual(expected, api.get_ranges([1, 3, 4, 5, 6]))

    def test_get_two_ranges(self):
        expected = [
            {'start': 1, 'end': 3},
            {'start': 456, 'end': 458}
        ]
        self.assertEqual(expected, api.get_ranges([1, 2, 3, 456, 457, 458]))

    def test_get_multi_ranges_and_single(self):
        expected = [
            {'start': 1, 'end': 3},
            {'start': 21, 'end': 21},
            {'start': 300, 'end': 300},
            {'start': 456, 'end': 458},
            {'start': 700000, 'end': 700000}
        ]
        self.assertEqual(
            expected, api.get_ranges([1, 2, 3, 21, 300, 456, 457, 458, 700000])
        )


class PeakFlowGraphDataTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        self.api = PeakFlowGraphData()
        self.patient, self.episode = self.new_patient_and_episode_please()
        request = self.rf.get("/")
        self.url = reverse(
            'peak_flow_graph_data-detail',
            kwargs=dict(pk=self.episode.id),
            request=request
        )
        self.assertTrue(
            self.client.login(
                username=self.user.username, password=self.PASSWORD
            )
        )

    def test_get_treatments(self):
        pfd = [
            {
                "day_num": 1,
                "treatment_taken": "Aspirin"
            },
            {
                "day_num": 2,
                "treatment_taken": "Aspirin"
            },
            {
                "day_num": 3,
                "treatment_taken": None
            },
            {
                "day_num": 4,
                "treatment_taken": "Paracetamol"
            }
        ]
        result = self.api.get_treatments(pfd)
        expected = {
            "Aspirin": [{
                "start": 1,
                "end": 2,
            }],
            "Paracetamol": [{
                "start": 4,
                "end": 4,
            }]
        }
        self.assertEqual(
            result,
            expected
        )

    def test_same_treatments_different_tranches(self):
        pfd = [
            {
                "day_num": 1,
                "treatment_taken": "Aspirin"
            },
            {
                "day_num": 2,
                "treatment_taken": "Aspirin"
            },
            {
                "day_num": 3,
                "treatment_taken": None
            },
            {
                "day_num": 4,
                "treatment_taken": "Aspirin"
            }
        ]
        result = self.api.get_treatments(pfd)
        expected = {
            "Aspirin": [
                {
                    "start": 1,
                    "end": 2,
                },
                {
                    "start": 4,
                    "end": 4,
                }
            ]
        }
        self.assertEqual(
            result,
            expected
        )

    def test_no_treatments(self):
        pfd = [
            {
                "day_num": 1,
                "treatment_taken": None
            },
            {
                "day_num": 2,
                "treatment_taken": None
            },
            {
                "day_num": 3,
                "treatment_taken": None
            },
            {
                "day_num": 4,
                "treatment_taken": None
            }
        ]
        result = self.api.get_treatments(pfd)
        expected = {}
        self.assertEqual(
            result,
            expected
        )

    def test_get_notes(self):
        self.episode.peakflowday_set.create(
            day_num=1,
            date=datetime.date(2019, 8, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            note="some notes"
        )

        self.episode.peakflowday_set.create(
            day_num=2,
            date=datetime.date(2019, 8, 4),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            flow_1300=700,
        )
        self.episode.peakflowday_set.create(
            day_num=3,
            date=datetime.date(2019, 8, 5),
        )
        self.episode.peakflowday_set.create(
            day_num=4,
            date=datetime.date(2019, 8, 6),
            note="other note"
        )
        notes = self.api.get_notes(self.episode.peakflowday_set.all())
        self.assertEqual(
            notes, "some notes"
        )

    def test_get_overrall_mean(self):
        self.episode.peakflowday_set.create(
            day_num=1,
            date=datetime.date(2019, 8, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
        )

        self.episode.peakflowday_set.create(
            day_num=2,
            date=datetime.date(2019, 8, 4),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            flow_1300=700,
            flow_1400=1000,
            flow_1500=900,
            flow_1600=900,
        )
        self.episode.peakflowday_set.create(
            day_num=3,
            date=datetime.date(2019, 8, 5),
        )
        m = self.api.get_overrall_mean(self.episode.peakflowday_set.all())
        self.assertEqual(
            m, 710
        )

    def test_get_overrall_mean_no_flows(self):
        self.episode.peakflowday_set.create(
            day_num=1,
            date=datetime.date(2019, 8, 3),
        )
        m = self.api.get_overrall_mean(self.episode.peakflowday_set.all())
        self.assertIsNone(m)

    def test_trial_data(self):
        self.maxDiff = None
        self.episode.peakflowday_set.create(
            day_num=1,
            date=datetime.date(2019, 8, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
        )

        self.episode.peakflowday_set.create(
            day_num=2,
            date=datetime.date(2019, 8, 4),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            flow_1300=700
        )
        result = self.api.trial_data(
            self.episode,
            1,
            self.episode.peakflowday_set.all()
        )
        expected = {
            'days': [
                {
                    'treatment_taken': None,
                    'day_num': 1,
                    'date': datetime.date(2019, 8, 3),
                    'work_day': False,
                    'pef_flow': None,
                    'min_flow': 500,
                    'mean_flow': 600,
                    'max_flow': 700,
                    'variabilty': 29,
                    'num_entries': 3
                },
                {
                    'treatment_taken': None,
                    'day_num': 2,
                    'date': datetime.date(2019, 8, 4),
                    'work_day': False,
                    'pef_flow': None,
                    'min_flow': 500,
                    'mean_flow': 625,
                    'max_flow': 700,
                    'variabilty': 29,
                    'num_entries': 4
                }
            ],
            'completeness': 50,
            'complete_days': 1,
            'treatments': {},
            'overrall_mean': 614,
            'pef_mean': None,
            'notes': "",
            'start_date': datetime.date(2019, 8, 3),
            'trial_num': 1
        }

        self.assertEqual(result, expected)

    def test_trial_data_with_one_day_with_no_entries(self):
        self.episode.peakflowday_set.create(
            day_num=1,
            date=datetime.date(2019, 8, 3)
        )
        result = self.api.trial_data(
            self.episode,
            1,
            self.episode.peakflowday_set.all()
        )
        expected = {
            'days': [{
                'date': datetime.date(2019, 8, 3),
                'day_num': 1,
                'max_flow': None,
                'mean_flow': None,
                'min_flow': None,
                'num_entries': None,
                'pef_flow': None,
                'treatment_taken': None,
                'variabilty': None,
                'work_day': False
            }],
            'completeness': 0,
            'complete_days': 0,
            'treatments': {},
            'overrall_mean': None,
            'pef_mean': None,
            'notes': "",
            'start_date': datetime.date(2019, 8, 3),
            'trial_num': 1
        }
        self.assertEqual(result, expected)

    def test_api(self):
        self.episode.peakflowday_set.create(
            trial_num=1,
            day_num=1,
            date=datetime.date(2019, 8, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            note="A note about trial 1"
        )
        self.episode.peakflowday_set.create(
            trial_num=1,
            day_num=2,
            date=datetime.date(2019, 8, 4),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            flow_1300=700
        )
        self.episode.peakflowday_set.create(
            trial_num=2,
            day_num=1,
            date=datetime.date(2019, 9, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            note="A note about trial 2"
        )
        response = self.client.get(self.url).json()
        # we don't want to double check that trial data
        # works but lets just make sure that
        # the data looks as we'd expect
        self.assertEqual(len(response[0]["days"]), 2)
        self.assertEqual(response[0]["trial_num"], 1)
        self.assertEqual(response[0]["notes"], "A note about trial 1")

        self.assertEqual(len(response[1]["days"]), 1)
        self.assertEqual(response[1]["trial_num"], 2)
        self.assertEqual(response[1]["notes"], "A note about trial 2")

    def test_api_ordering(self):
        """
        The list we return should be ordered by trial start date
        """
        self.episode.peakflowday_set.create(
            trial_num=1,
            day_num=1,
            date=datetime.date(2019, 10, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            note="A note about trial 1"
        )
        self.episode.peakflowday_set.create(
            trial_num=1,
            day_num=2,
            date=datetime.date(2019, 10, 4),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            flow_1300=700
        )
        self.episode.peakflowday_set.create(
            trial_num=2,
            day_num=1,
            date=datetime.date(2019, 9, 3),
            flow_1000=500,
            flow_1100=600,
            flow_1200=700,
            note="A note about trial 2"
        )
        response = self.client.get(self.url).json()
        self.assertEqual(response[0]["trial_num"], 2)
        self.assertEqual(response[1]["trial_num"], 1)
