import datetime
from plugins.lab.models import Bloods
from django.urls import reverse
from opal.core.test import OpalTestCase
from plugins.lab import views


class LabMonthReviewTestCase(OpalTestCase):
    def setUp(self):
        self.view = views.LabMonthReview()
        self.url = reverse(
            "lab-month-review",
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
