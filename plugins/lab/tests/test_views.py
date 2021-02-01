import datetime
from opal.core.test import OpalTestCase
from plugins.lab import views


class LabMonthReviewTestCase(OpalTestCase):
    def setUp(self):
        self.view = views.LabMonthReview()

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
