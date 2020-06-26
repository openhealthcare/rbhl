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


class DiagnosisTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        patient, self.episode = self.new_patient_and_episode_please()
        self.today = datetime.date.today()

    def test_creation_of_asthma_details_should_create_diagnosis(self):
        """
        When you create an AsthmaDetail model it should
        create a corresponding diagnosis
        """
        self.episode.asthmadetails_set.create(date=self.today)
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.ASTHMA,
        )
        self.assertEqual(
            self.episode.diagnosis_set.get().date,
            self.today,
        )

    def test_editing_asthma_details(self):
        """
        Editing the asthma details multiple times
        should not create multiple asthma diagnosis
        """
        asthma = self.episode.asthmadetails_set.create()
        asthma.trigger = "something"
        asthma.save()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.ASTHMA
        )

    def test_editing_asthma_should_update_date(self):
        """
        If a patient has multiple asthma diagnosis. When
        we edit we should only update diagnosis related to
        the asthma that is being updated
        """
        yesterday = self.today - datetime.timedelta(1)
        two_days_ago = self.today - datetime.timedelta(2)
        asthma_to_be_updated = self.episode.asthmadetails_set.create(
            date=yesterday
        )
        diagnosis_to_be_updated = self.episode.diagnosis_set.get()
        self.episode.asthmadetails_set.create(
            date=two_days_ago
        )
        asthma_to_be_updated.date = self.today
        asthma_to_be_updated.save()

        self.assertEqual(
            models.Diagnosis.objects.count(), 2
        )
        self.assertEqual(
            models.Diagnosis.objects.get(id=diagnosis_to_be_updated.id).date,
            self.today
        )

    def test_creation_of_rhinitis_details_should_create_diagnosis(self):
        """
        When you create an RhinitisDetails model it should
        create a corresponding diagnosis
        """
        self.episode.rhinitisdetails_set.create(date=self.today)
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.RHINITIS
        )
        self.assertEqual(
            self.episode.diagnosis_set.get().date,
            self.today,
        )

    def test_editing_rhinitis_details(self):
        """
        Editing the rhinitis details multiple times
        should not create multiple rhinits diagnosis
        """
        rhinitis = self.episode.rhinitisdetails_set.create()
        rhinitis.trigger = "something"
        rhinitis.save()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.RHINITIS
        )

    def test_editing_rhinitis_should_update_date(self):
        """
        If a patient has multiple rhinitis diagnosis. When
        we edit we should only update the diagnosis related to
        the rhinitis that is being updated
        """
        yesterday = self.today - datetime.timedelta(1)
        two_days_ago = self.today - datetime.timedelta(2)
        rhinitis_to_be_updated = self.episode.rhinitisdetails_set.create(
            date=yesterday
        )
        diagnosis_to_be_updated = self.episode.diagnosis_set.get()
        self.episode.rhinitisdetails_set.create(
            date=two_days_ago
        )
        rhinitis_to_be_updated.date = self.today
        rhinitis_to_be_updated.save()

        self.assertEqual(
            models.Diagnosis.objects.count(), 2
        )
        self.assertEqual(
            models.Diagnosis.objects.get(id=diagnosis_to_be_updated.id).date,
            self.today
        )

    def test_deletion_of_asthma_details_should_delete_diagnosis(self):
        """
        When we delete asthma details we should delete the diagnosis of asthma
        """
        self.episode.asthmadetails_set.create()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.ASTHMA
        )
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.MALIGNANCY,
        )
        self.episode.asthmadetails_set.all().delete()
        self.assertFalse(self.episode.asthmadetails_set.exists())
        self.assertEqual(
            self.episode.diagnosis_set.get().category, models.Diagnosis.MALIGNANCY
        )

    def test_deletion_of_rhinitis_details_should_delete_diagnosis(self):
        """
        When we delete rhinits details we should delete the diagnosis of rhinits
        """
        self.episode.rhinitisdetails_set.create()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.RHINITIS
        )
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.MALIGNANCY,
        )
        self.episode.rhinitisdetails_set.all().delete()
        self.assertFalse(self.episode.rhinitisdetails_set.exists())
        self.assertEqual(
            self.episode.diagnosis_set.get().category, models.Diagnosis.MALIGNANCY
        )

    def test_creation_of_nad_should_delete_other_diagnosis(self):
        """
        A patient who is NAD should have no other diagnosis
        """
        self.episode.diagnosis_set.create(
            category="other", condition="bad knee"
        )
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.NAD
        )

    def test_creation_of_nad_should_delete_asthma(self):
        """
        A patient who is NAD should have no asthma details
        """
        self.episode.asthmadetails_set.create()
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.assertFalse(self.episode.asthmadetails_set.exists())

    def test_creation_of_nad_should_delete_rhinits(self):
        """
        A patient who is NAD should have no rhinitis details
        """
        self.episode.rhinitisdetails_set.create()
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.assertFalse(self.episode.rhinitisdetails_set.exists())

    def test_creation_of_asthma_should_delete_nad(self):
        """
        A patient who is has asthma details cannot be NAD
        """
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.episode.asthmadetails_set.create()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.ASTHMA
        )

    def test_creation_of_rhinitis_should_delete_nad(self):
        """
        A patient who is has rhinitis details cannot be NAD
        """
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.episode.rhinitisdetails_set.create()
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.RHINITIS
        )

    def test_creation_of_other_diagnosis_should_delete_nad(self):
        """
        A patient who is has other diagnosis cannot be NAD
        """
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.NAD,
        )
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.MALIGNANCY,
        )
        self.assertEqual(
            self.episode.diagnosis_set.get().category,
            models.Diagnosis.MALIGNANCY
        )

    def multiple_diagnosis_that_are_not_nad_are_ok(self):
        self.episode.asthmadetails_set.create()
        self.episode.rhinitisdetails_set.create()
        self.episode.diagnosis_set.create(
            category=models.Diagnosis.MALIGNANCY,
        )
        self.assertEqual(
            {
                models.Diagnosis.ASTHMA,
                models.Diagnosis.RHINITIS,
                models.Diagnosis.MALIGNANCY,
            },
            set(
                self.episode.diagnosis.values_list('category_name', flat=True)
            )
        )


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
        display_name = models.PeakFlowDay.get_display_name()
        self.assertEqual(
            display_name, "Peak flow day"
        )

    def test_get_display_name_verbose_name_override(self):
        display_name = models.ClinicLog.get_display_name()
        self.assertEqual(
            display_name, "Clinic details"
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
