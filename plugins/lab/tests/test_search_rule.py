import json
from django.urls import reverse
from opal.core.test import OpalTestCase
from plugins.lab.models import Allergen
from plugins.lab.search_rule import AllergenSearchField, BloodResults


class SearchRuleFieldTestCase(OpalTestCase):
    def test_different_patients_with_fk_and_ft(self):
        # a patient with mouse fk
        patient1, episode_fk_with_mouse = self.new_patient_and_episode_please()
        Allergen.objects.create(name="mouse")
        bloods = patient1.bloods_set.create()
        blood_result = bloods.bloodresult_set.create()
        blood_result.allergen = "mouse"
        blood_result.save()

        # a patient with mouse ft
        patient2, episode_ft_with_mouse = self.new_patient_and_episode_please()
        bloods = patient2.bloods_set.create()
        blood_result = bloods.bloodresult_set.create(allergen_ft="mouse stuff")

        # a patient with neither
        patient3, _ = self.new_patient_and_episode_please()
        bloods = patient3.bloods_set.create()
        blood_result = bloods.bloodresult_set.create(allergen_ft="rat stuff")

        query = {"queryType": "Contains", "query": "mouse"}
        result = AllergenSearchField().query(query)
        self.assertEqual(
            set(result), set([episode_fk_with_mouse, episode_ft_with_mouse])
        )


class IntegrationSearchRuleTestCase(OpalTestCase):
    """
    Integration tests that make sure opal upgrades do not break our search rule.

    We expect the extract schema to return the blood results metadata.

    We expect to be able to search by blood result allergen and to
    get an appropriate response.
    """
    def setUp(self):
        self.client.login(username=self.user.username, password=self.PASSWORD)

    def test_get_extract_schema(self):
        schema_url = reverse("extract-schema-list")
        result = self.client.get(schema_url)
        self.assertEqual(result.status_code, 200)
        blood_results = [i for i in result.json() if i["name"] == BloodResults.slug]
        expected = [
            {
                "name": "blood_results",
                "display_name": "Blood Results",
                "advanced_searchable": True,
                "fields": [
                    {
                        "name": "allergen",
                        "title": "Allergen",
                        "type": "string",
                        "enum": None,
                        "lookup_list": "allergen",
                        "description": None,
                    }
                ],
            }
        ]
        self.assertEqual(blood_results, expected)

    def test_from_post_request(self):
        url = reverse('extract_search')
        patient, _ = self.new_patient_and_episode_please()
        patient.demographics_set.update(first_name='Sarah')
        Allergen.objects.create(name="mouse")
        bloods = patient.bloods_set.create()
        blood_result = bloods.bloodresult_set.create()
        blood_result.allergen = "mouse"
        blood_result.save()

        query = json.dumps([{
            "queryType": "Equals",
            "query": 'Mouse',
            "field": "allergen",
            'combine': 'and',
            'column': u'blood_results',
        }])
        response = self.client.generic('POST', url, query)
        self.assertEqual(response.status_code, 200)
        result = response.json()["object_list"]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["first_name"], "Sarah")
