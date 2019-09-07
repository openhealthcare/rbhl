from opal.core.test import OpalTestCase
from rbhl.api import PeakFlowGraphData


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
                "treatment_taken": "Paracetomol"
            }
        ]
        result = self.api.get_treatments(pfd)
        expected = {
            "Aspirin": [{
                "start": 1,
                "end": 2,
            }],
            "Paracetomol": [{
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
