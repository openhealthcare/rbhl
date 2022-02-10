import datetime
from django.urls import reverse
from opal.core.test import OpalTestCase
from opal.models import Role
from rbhl import constants


class PatientListsTestCase(OpalTestCase):
    def setUp(self):
        self.client.login(
            username=self.user.username, password=self.PASSWORD
        )
        self.active_url = reverse(
            "active-list",
        )
        self.seen_by_me_url = reverse(
            "seen-by-me-list",
        )

    def test_active_list_when_populated(self):
        _, episode = self.new_patient_and_episode_please()
        cl = episode.cliniclog_set.first()
        cl.active = True
        cl.save()
        result = self.client.get(self.active_url)
        self.assertEqual(
            result.status_code, 200
        )
        context = result.context
        self.assertEqual(
            context["object_list"].get().id,
            episode.id
        )

    def test_active_list_when_not_populated(self):
        result = self.client.get(self.active_url)
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
        object_list = self.client.get(self.active_url).context["object_list"]
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
        url = self.active_url + "?order=seen_by"
        object_list = self.client.get(url).context["object_list"]
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
        url = self.active_url + "?order=-seen_by"
        object_list = self.client.get(url).context["object_list"]
        self.assertEqual(
            list(object_list), [third_episode, second_episode, first_episode]
        )

    def test_seen_by_me_list_with_initials(self):
        user = self.user
        user.first_name = "Jane"
        user.last_name = "Doe"
        user.save()
        role = Role.objects.get(name=constants.DOCTOR_ROLE)
        user.profile.roles.add(role)
        _, episode = self.new_patient_and_episode_please()
        episode.cliniclog_set.update(active=True, seen_by="jd")
        context = self.client.get(self.seen_by_me_url).context
        object_list = context["object_list"]
        self.assertEqual(
            list(object_list), [episode]
        )
        self.assertEqual(
            context["initials"], "JD"
        )

    def test_seen_by_me_list_for_user_without_initials(self):
        user = self.user
        user.first_name = ""
        user.last_name = ""
        user.save()
        _, episode = self.new_patient_and_episode_please()
        episode.cliniclog_set.update(active=True, seen_by="jd")
        context = self.client.get(self.seen_by_me_url).context
        object_list = context["object_list"]
        self.assertEqual(
            list(object_list), []
        )
        self.assertEqual(
            context["initials"], ""
        )
