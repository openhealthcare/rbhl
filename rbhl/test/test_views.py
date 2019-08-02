import datetime
from django.urls import reverse
from opal.core.test import OpalTestCase


class PatientListsTestCase(OpalTestCase):
    def setUp(self):
        self.client.login(
            username=self.user.username, password=self.PASSWORD
        )
        self.url = reverse(
            "active-list",
        )

    def test_active_list_when_populated(self):
        _, episode = self.new_patient_and_episode_please()
        cl = episode.cliniclog_set.first()
        cl.active = True
        cl.save()
        result = self.client.get(self.url)
        self.assertEqual(
            result.status_code, 200
        )
        context = result.context
        self.assertEqual(
            context["object_list"].get().id,
            episode.id
        )

    def test_active_list_when_not_populated(self):
        result = self.client.get(self.url)
        self.assertEqual(
            result.status_code, 200
        )
        context = result.context
        self.assertEqual(
            context["object_list"].count(),
            0
        )

    def test_default_ordering(self):
        # lets make sure ids don't get accidentally confused for ordering
        _, third_episode = self.new_patient_and_episode_please()
        _, first_episode = self.new_patient_and_episode_please()
        _, second_episode = self.new_patient_and_episode_please()

        today = datetime.date.today()
        first_dt = today - datetime.timedelta(10)
        second_dt = today - datetime.timedelta(5)
        third_dt = today

        third_episode.cliniclog_set.update(
            active=True,
            clinic_date=third_dt
        )
        first_episode.cliniclog_set.update(
            active=True,
            clinic_date=first_dt
        )
        second_episode.cliniclog_set.update(
            active=True,
            clinic_date=second_dt
        )
        object_list = self.client.get(self.url).context["object_list"]
        self.assertEqual(
            list(object_list), [first_episode, second_episode, third_episode]
        )

    def test_ascending_ordering(self):
        # lets make sure ids don't get accidentally confused for ordering
        _, third_episode = self.new_patient_and_episode_please()
        _, first_episode = self.new_patient_and_episode_please()
        _, second_episode = self.new_patient_and_episode_please()

        third_episode.cliniclog_set.update(
            active=True,
            seen_by="Zara"
        )
        first_episode.cliniclog_set.update(
            active=True,
            seen_by="Anne"
        )
        second_episode.cliniclog_set.update(
            active=True,
            seen_by="Jane"
        )
        self.url = self.url + "?order=seen_by"
        object_list = self.client.get(self.url).context["object_list"]
        self.assertEqual(
            list(object_list), [first_episode, second_episode, third_episode]
        )

    def test_descending_ordering(self):
        # lets make sure ids don't get accidentally confused for ordering
        _, third_episode = self.new_patient_and_episode_please()
        _, first_episode = self.new_patient_and_episode_please()
        _, second_episode = self.new_patient_and_episode_please()

        third_episode.cliniclog_set.update(
            active=True,
            seen_by="Zara"
        )
        first_episode.cliniclog_set.update(
            active=True,
            seen_by="Anne"
        )
        second_episode.cliniclog_set.update(
            active=True,
            seen_by="Jane"
        )
        self.url = self.url + "?order=-seen_by"
        object_list = self.client.get(self.url).context["object_list"]
        self.assertEqual(
            list(object_list), [third_episode, second_episode, first_episode]
        )
