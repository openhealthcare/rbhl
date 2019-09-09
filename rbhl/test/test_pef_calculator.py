from opal.core.test import OpalTestCase
from rbhl import pef_calculator


class PefCalculatorTestCase(OpalTestCase):
    def setUp(self):
        self.age = 38
        self.height = 172.72

    def test_male(self):
        self.assertEqual(
            pef_calculator.calculate_pef(
                self.age, self.height, "Male"
            ),
            634
        )

    def test_female(self):
        self.assertEqual(
            pef_calculator.calculate_pef(
                self.age, self.height, "Female"
            ),
            493
        )

    def test_unknown(self):
        with self.assertRaises(ValueError):
            pef_calculator.calculate_pef(
                self.age, self.height, None
            )
        with self.assertRaises(ValueError):
            pef_calculator.calculate_pef(
                self.age, self.height, ""
            )
        with self.assertRaises(ValueError):
            pef_calculator.calculate_pef(
                self.age, self.height, "other"
            )
