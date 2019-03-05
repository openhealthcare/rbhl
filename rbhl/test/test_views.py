from opal.core.test import OpalTestCase
from rbhl import patient_lists
from django.urls import reverse


class PatientListsTestCase(OpalTestCase):
    def setUp(self):
        self.client.login(
            username=self.user.username, password=self.PASSWORD
        )

    def test_active_list_when_populated(self):
        url = reverse(
            "static-list",
            kwargs=dict(
                slug=patient_lists.ActivePatients.get_slug()
            )
        )
        _, episode = self.new_patient_and_episode_please()
        cl = episode.cliniclog_set.first()
        cl.active = True
        cl.save()
        result = self.client.get(url)
        self.assertEqual(
            result.status_code, 200
        )
        context = result.context
        self.assertEqual(
            context["object_list"].get().id,
            episode.id
        )

    def test_active_list_when_not_populated(self):
        url = reverse(
            "static-list",
            kwargs=dict(
                slug=patient_lists.ActivePatients.get_slug()
            )
        )
        result = self.client.get(url)
        self.assertEqual(
            result.status_code, 200
        )
        context = result.context
        self.assertEqual(
            context["object_list"].count(),
            0
        )
