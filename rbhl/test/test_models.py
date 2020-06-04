import datetime
from unittest import mock
from opal.core.test import OpalTestCase
from rbhl import models


class CalculatePEFTestCase(OpalTestCase):
    def test_calculate_pef_male_1(self):
        result = models.calculate_peak_expiratory_flow(
            height=170, age=35, sex="Male"
        )
        self.assertEqual(result, 630)

    def test_calculate_pef_male_2(self):
        result = models.calculate_peak_expiratory_flow(
            height=180, age=30, sex="Male"
        )
        self.assertEqual(result, 641)

    def test_calculate_pef_male_3(self):
        result = models.calculate_peak_expiratory_flow(
            height=150, age=64, sex="Male"
        )
        self.assertEqual(result, 533)

    def test_calculate_pef_female_1(self):
        result = models.calculate_peak_expiratory_flow(
            height=140, age=35, sex="Female"
        )
        self.assertEqual(result, 456)

    def test_calculate_pef_female_2(self):
        result = models.calculate_peak_expiratory_flow(
            height=180, age=30, sex="Female"
        )
        self.assertEqual(result, 502)

    def test_calculate_pef_female_3(self):
        result = models.calculate_peak_expiratory_flow(
            height=150, age=64, sex="Female"
        )
        self.assertEqual(result, 415)


class GetPeakExpiratoryFlowTestCase(OpalTestCase):
    def setUp(self):
        patient, self.episode = self.new_patient_and_episode_please()
        self.demographics = patient.demographics()

    def test_with_demographics_age(self):
        self.demographics.date_of_birth = datetime.date(1990, 12, 1)
        self.demographics.sex = "Male"
        self.demographics.height = 180
        self.demographics.save()
        expected = models.get_peak_expiratory_flow(
            datetime.date(2019, 12, 1), self.episode, "1"
        )
        self.assertEqual(
            expected, 638
        )

    def test_with_imported_from_database_age(self):
        self.demographics.date_of_birth = None
        self.demographics.sex = "Male"
        self.demographics.height = 180
        self.demographics.save()
        self.episode.importedfrompeakflowdatabase_set.create(
            age="29", trial_number="1"
        )
        expected = models.get_peak_expiratory_flow(
            datetime.date(2019, 12, 1), self.episode, "1"
        )
        self.assertEqual(
            expected, 638
        )

    def test_with_no_age(self):
        self.demographics.date_of_birth = None
        self.demographics.sex = "Male"
        self.demographics.height = 180
        self.demographics.save()
        expected = models.get_peak_expiratory_flow(
            datetime.date(2019, 12, 1), self.episode, "1"
        )
        self.assertIsNone(expected)

    def test_with_no_sex(self):
        self.demographics.date_of_birth = datetime.date(1990, 12, 1)
        self.demographics.sex = None
        self.demographics.height = 180
        self.demographics.save()
        expected = models.get_peak_expiratory_flow(
            datetime.date(2019, 12, 1), self.episode, "1"
        )
        self.assertIsNone(expected)

    def test_with_no_height(self):
        self.demographics.date_of_birth = datetime.date(1990, 12, 1)
        self.demographics.sex = "Male"
        self.demographics.height = None
        self.demographics.save()
        expected = models.get_peak_expiratory_flow(
            datetime.date(2019, 12, 1), self.episode, "1"
        )
        self.assertIsNone(expected)


class RBHLSubrecordTestCase(OpalTestCase):
    def test_get_field_title(self):
        self.assertTrue(issubclass(models.Referral, models.RBHLSubrecord))
        field_title = models.Referral._get_field_title("referrer_title")
        self.assertEqual(
            field_title, "Referrer title"
        )

    def test_get_field_title_verbose_name_override(self):
        self.assertTrue(issubclass(models.Employment, models.RBHLSubrecord))
        field_title = models.Employment._get_field_title("oh_provider")
        self.assertEqual(
            field_title, "OH provider"
        )

    def test_get_display_name(self):
        self.assertTrue(issubclass(models.ClinicLog, models.RBHLSubrecord))
        display_name = models.ClinicLog.get_display_name()
        self.assertEqual(
            display_name, "Clinic log"
        )

    def test_get_display_name_verbose_name_override(self):
        with mock.patch.object(models.ClinicLog, "_meta"):
            models.ClinicLog._meta.verbose_name = "Something"
            display_name = models.ClinicLog.get_display_name()
        self.assertEqual(
            display_name, "Something"
        )


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
            aggregate_data["num_entries"], 3
        )

    def test_get_aggregate_data_num_entries(self):
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
            aggregate_data["num_entries"], 5
        )

    def test_get_aggregate_data_none(self):
        pfd = self.episode.peakflowday_set.create()
        aggregate_data = pfd.get_aggregate_data()
        self.assertIsNone(aggregate_data)
