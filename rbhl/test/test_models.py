from opal.core.test import OpalTestCase
from rbhl import models


class CalculatePEFTestCase(OpalTestCase):
    def test_calculate_pef_male(self):
        result = models.calculate_peak_expiratory_flow(
            height=170, age=35, sex="Male"
        )
        self.assertEqual(result, 630.3)

    def test_calculate_pef_female(self):
        result = models.calculate_peak_expiratory_flow(
            height=140, age=35, sex="Female"
        )
        self.assertEqual(result, 456.37)
