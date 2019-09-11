"""
Unittests for rbhl.api
"""
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
        self.assertEqual(expected, api.get_ranges([1,3]))

    def test_get_range(self):
        self.assertEqual([{'start': 1, 'end': 3}], api.get_ranges([1,2,3]))
        self.assertEqual([{'start': 1, 'end': 5}], api.get_ranges([1,2,3,4,5]))
        self.assertEqual([{'start': 1, 'end': 9}], api.get_ranges([1,2,3,4,5,6,7,8,9]))

    def test_get_single_and_range(self):
        expected = [
            {'start': 1, 'end': 1},
            {'start': 3, 'end': 6}
        ]
        self.assertEqual(expected, api.get_ranges([1,3,4,5,6]))

    def test_get_two_ranges(self):
        expected = [
            {'start': 1,   'end': 3},
            {'start': 456, 'end': 458}
        ]
        self.assertEqual(expected, api.get_ranges([1,2,3,456,457,458]))

    def test_get_multi_ranges_and_single(self):
        expected = [
            {'start': 1,      'end': 3},
            {'start': 21,     'end': 21},
            {'start': 300,    'end': 300},
            {'start': 456,    'end': 458},
            {'start': 700000, 'end': 700000}
        ]
        self.assertEqual(expected, api.get_ranges([1,2,3,21,300,456,457,458,700000]))



class PeakFlowGraphDataTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        self.api = PeakFlowGraphData()

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
