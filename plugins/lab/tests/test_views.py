import datetime
from plugins.lab.models import Bloods
from django.urls import reverse
from opal.core.test import OpalTestCase
from plugins.lab import views


class LabMonthActivityTestCase(OpalTestCase):
    def setUp(self):
        self.view = views.LabMonthActivity()
        self.url = reverse(
            "lab-month-activity",
            kwargs={
                "year": "2121",
                "month": "1"
            }
        )

    def test_get_days(self):
        # Monday
        start_dt = datetime.date(2021, 2, 1)
        # End Monday
        end_dt = datetime.date(2021, 2, 8)

        # start date to end date inclusive
        # excluding weekends
        self.assertEqual(
            self.view.get_day_count(start_dt, end_dt), 6
        )

    def test_get_days_same_day(self):
        # Monday
        start_dt = datetime.date(2021, 2, 1)
        end_dt = datetime.date(2021, 2, 1)

        # start date to end date inclusive
        # excluding weekends
        self.assertEqual(
            self.view.get_day_count(start_dt, end_dt), 1
        )

    def test_skips_bank_holidays(self):
        # should skip the may day bank holiday
        # it always occurs in the first week of may
        # therefore in the first week of may there
        # should always be 4 work days, (2 weekends, 1 bank holiday)
        year = datetime.date.today().year
        start_dt = datetime.date(year, 5, 1)
        end_dt = datetime.date(year, 5, 7)
        self.assertEqual(
            self.view.get_day_count(start_dt, end_dt), 4
        )

    def test_get_multi_mode(self):
        self.assertEqual(
            self.view.get_multi_mode([]), None
        )
        self.assertEqual(
            self.view.get_multi_mode([1]), [1]
        )
        self.assertEqual(
            self.view.get_multi_mode([1, 2]), [1, 2]
        )
        self.assertEqual(
            self.view.get_multi_mode([1, 2, 2]), [2]
        )

    def test_get(self):
        patient, _ = self.new_patient_and_episode_please()
        bloods = Bloods.objects.create(
            patient=patient,
            blood_date=datetime.date(2021, 1, 10),
            report_st=datetime.date(2021, 1, 11),
            blood_number="111"
        )
        bloods.exposure = "grass"
        bloods.save()
        result = bloods.bloodresult_set.create()
        result.allergen = "Timothy"
        result.save()
        # initialise the user property
        self.user
        self.client.login(
            username=self.USERNAME, password=self.PASSWORD
        )
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, 200)

    def test_get_results_rows(self):
        patient, _ = self.new_patient_and_episode_please()
        bloods = Bloods.objects.create(
            patient=patient,
            blood_date=datetime.date(2021, 1, 10),
            report_st=datetime.date(2021, 1, 11),
            blood_number="111"
        )
        result = bloods.bloodresult_set.create()
        result.allergen = 'flour'
        result.kul = 3
        result.save()
        bloods.exposure = "grass"
        bloods.save()
        result = bloods.bloodresult_set.create()
        result.allergen = "Timothy"
        result.save()
        rows = views.LabMonthActivity().get_results_rows(1, 2021)
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            rows[0]["Blood num"], "111"
        )


class LabOverviewTestCase(OpalTestCase):
    def setUp(self):
        self.view = views.LabMonthActivity()
        self.url = reverse("lab-overview")

    def test_get(self):
        patient, _ = self.new_patient_and_episode_please()
        bloods = Bloods.objects.create(
            patient=patient,
            blood_date=datetime.date(2021, 1, 10),
            report_st=datetime.date(2021, 1, 11),
            blood_number="111"
        )
        bloods.exposure = "grass"
        bloods.save()
        result = bloods.bloodresult_set.create()
        result.allergen = "Timothy"
        result.save()
        # initialise the user property
        self.user
        self.client.login(
            username=self.USERNAME, password=self.PASSWORD
        )
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, 200)
