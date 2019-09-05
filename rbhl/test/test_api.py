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
        expected = [
            {
                "start": 1,
                "end": 2,
                "treatment": "Aspirin"
            },
            {
                "start": 4,
                "end": 4,
                "treatment": "Paracetomol"
            }
        ]
        self.assertEqual(
            result,
            expected
        )
