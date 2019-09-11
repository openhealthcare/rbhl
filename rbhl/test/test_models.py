import datetime
from unittest import mock
from opal.core.test import OpalTestCase
from rbhl import models


class CalculatePEFTestCase(OpalTestCase):
    def test_calculate_pef_male(self):
        result = models.calculate_peak_expiratory_flow(
            height=170, age=35, sex="Male"
        )
        self.assertEqual(result, 630)

    def test_calculate_pef_female(self):
        result = models.calculate_peak_expiratory_flow(
            height=140, age=35, sex="Female"
        )
        self.assertEqual(result, 456)


class DemographicsTestCase(OpalTestCase):
    def setUp(self):
        patient, _ = self.new_patient_and_episode_please()
        self.demographics = patient.demographics()

    @mock.patch("rbhl.models.datetime")
    def test_age(self, dt):
        dt.date.today.return_value = datetime.date(2019, 12, 1)
        self.demographics.date_of_birth = datetime.date(1990, 12, 1)
        self.demographics.save()
        self.assertEqual(self.demographics.get_age(), 29)
        self.assertEqual(
            self.demographics.get_age(datetime.date(2009, 11, 30)),
            18
        )
        self.assertEqual(
            self.demographics.get_age(datetime.date(2009, 12, 1)),
            19
        )
        self.assertEqual(
            self.demographics.get_age(datetime.date(2009, 12, 2)),
            19
        )

    def test_pef(self):
        self.demographics.date_of_birth = datetime.date(1990, 12, 1)
        self.demographics.sex = "Male"
        self.demographics.height = 180
        self.demographics.save()
        expected = self.demographics.get_pef(datetime.date(2019, 12, 1))
        self.assertEqual(
            expected, 638
        )
