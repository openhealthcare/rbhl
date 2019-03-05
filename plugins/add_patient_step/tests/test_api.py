from unittest import mock
from django.urls import reverse
from django.test import override_settings
from opal.core.test import OpalTestCase
from plugins.add_patient_step.api import DemographicsSearch


@mock.patch("plugins.add_patient_step.api.import_string")
class DemographicsSearchTestCase(OpalTestCase):
    def setUp(self):
        self.naked_url = reverse("demographics-search-list")
        self.client.login(
            username=self.user.username, password=self.PASSWORD
        )
        self.url = "{}?hospital_number=111".format(self.naked_url)

    @override_settings(UPSTREAM_DEMOGRAPHICS_SERVICE="blah")
    def test_no_hospital_number(self, import_string):
        response = self.client.get(self.naked_url)
        self.assertEqual(
            response.status_code, 400
        )
        self.assertFalse(import_string.called)

    @override_settings(UPSTREAM_DEMOGRAPHICS_SERVICE="blah")
    def test_patient_found_locally(self, import_string):
        patient, episde = self.new_patient_and_episode_please()
        patient.demographics_set.update(
            hospital_number="111",
            first_name="Jane"
        )
        expected = self.client.get(self.url)
        self.assertEqual(
            expected.status_code, 200
        )
        result = expected.data
        self.assertEqual(
            result["status"], DemographicsSearch.PATIENT_FOUND_IN_APPLICATION
        )
        self.assertEqual(result["patient"]["id"], patient.id)
        self.assertFalse(import_string.called)

    @override_settings(UPSTREAM_DEMOGRAPHICS_SERVICE="blah")
    def test_patient_found_in_upstream_service(self, import_string):
        returned = {
            "hospital_number": "111",
            "first_name": "Jane"
        }
        import_string.return_value = lambda x: returned
        expected = self.client.get(self.url)
        self.assertEqual(
            expected.status_code, 200
        )
        result = expected.data
        self.assertEqual(
            result["status"], DemographicsSearch.PATIENT_FOUND_UPSTREAM
        )
        self.assertEqual(
            result["patient"]["demographics"][0]["first_name"],
            "Jane"
        )
        import_string.assert_called_once("blah")

    @override_settings(UPSTREAM_DEMOGRAPHICS_SERVICE=None)
    def test_patient_not_found(self, import_string):
        expected = self.client.get(self.url)
        self.assertEqual(expected.status_code, 200)
        self.assertEqual(
            expected.data["status"], DemographicsSearch.PATIENT_NOT_FOUND
        )
