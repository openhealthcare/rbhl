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


class PeakFlowDayTestCase(OpalTestCase):
    def setUp(self):
        _, self.episode = self.new_patient_and_episode_please()

    def test_get_aggregate_data(self):
        pfd = self.episode.peakflowday_set.create(
            flow_1000=400,
            flow_1100=500,
            flow_1200=600
        )

        aggregate_data = pfd.get_aggregate_data()
        self.assertEqual(
            aggregate_data["min_flow"], 400
        )

        self.assertEqual(
            aggregate_data["max_flow"], 600
        )

        self.assertEqual(
            aggregate_data["mean_flow"], 500
        )

        self.assertEqual(
            aggregate_data["variabilty"], 33
        )

        self.assertEqual(
            aggregate_data["completeness"], False
        )

    def test_get_aggregate_data_complete(self):
        pfd = self.episode.peakflowday_set.create(
            flow_1000=400,
            flow_1100=500,
            flow_1200=600,
            flow_1300=600,
            flow_1400=600
        )

        aggregate_data = pfd.get_aggregate_data()
        self.assertEqual(
            aggregate_data["min_flow"], 400
        )

        self.assertEqual(
            aggregate_data["max_flow"], 600
        )

        self.assertEqual(
            aggregate_data["mean_flow"], 540
        )

        self.assertEqual(
            aggregate_data["variabilty"], 33
        )

        self.assertEqual(
            aggregate_data["completeness"], True
        )

    def test_get_aggregate_data_none(self):
        pfd = self.episode.peakflowday_set.create()
        aggregate_data = pfd.get_aggregate_data()
        self.assertIsNone(aggregate_data)
