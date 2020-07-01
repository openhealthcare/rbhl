import datetime
from opal.core.test import OpalTestCase
from plugins.lab.models import Specimen, Observation


class SpecimenTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.patient, _ = self.new_patient_and_episode_please()

    def create_specimen(self):
        specimen = self.patient.specimen_set.create()
        specimen.reference_number = ''
        specimen.blood_date = datetime.date(2020, 3, 27)
        specimen.exposure = 'HOUSE DUST MITES'
        lab_test = specimen.labtest_set.create()
        lab_test.test_name = 'D. PTERONYSSINUS'
        lab_test.save()
        observation = lab_test.observation_set.create()
        observation.observation_name = "kul"
        observation.observation_value = '< 0.1'
        observation.save()

        observation = lab_test.observation_set.create()
        observation.observation_name = "klass"
        observation.observation_value = '0'
        observation.save()
        return specimen

    def test_to_dict(self):
        specimen = self.create_specimen()
        result = specimen.to_dict(self.user)

        # check the specimen model itself serializes
        self.assertEqual(
            result["blood_date"], datetime.date(2020, 3, 27)
        )

        # check lab tests serialize
        self.assertEqual(len(result["labtest_set"]), 1)
        self.assertEqual(
            result["labtest_set"][0]["test_name"], "D. PTERONYSSINUS"
        )

        # check observations serialize
        self.assertEqual(len(result["labtest_set"][0]["observation_set"]), 2)
        expected_observations = set({"kul", "klass"})
        found_observations = set([
            i["observation_name"] for i in result["labtest_set"][0]["observation_set"]
        ])
        self.assertEqual(expected_observations, found_observations)

    def test_update_from_dict_specimen(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        as_dict["blood_date"] = datetime.date(2020, 3, 28)
        specimen.update_from_dict(as_dict, user=self.user)
        reloaded = Specimen.objects.get(id=specimen.id)
        self.assertEqual(
            reloaded.blood_date, datetime.date(2020, 3, 28)
        )

    def test_update_from_dict_update_lab_test(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        as_dict["labtest_set"][0]["test_name"] = 'DUST MITES'
        specimen.update_from_dict(as_dict, user=self.user)
        reloaded = Specimen.objects.get(id=specimen.id)
        self.assertEqual(
            reloaded.labtest_set.get().test_name,
            "DUST MITES"
        )

    def test_update_from_dict_delete_lab_test(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        as_dict["labtest_set"] = []
        specimen.update_from_dict(as_dict, user=self.user)
        reloaded = Specimen.objects.get(id=specimen.id)
        self.assertFalse(reloaded.labtest_set.exists())

    def test_update_from_dict_create_lab_test(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        as_dict["labtest_set"][0].pop("id")
        as_dict["labtest_set"][0]["observation_set"] = [{
            "observation_name": "COMMENT"
        }]
        specimen.labtest_set.all().delete()
        specimen.update_from_dict(as_dict, user=self.user)
        reloaded = Specimen.objects.get(id=specimen.id)
        self.assertEqual(
            reloaded.labtest_set.get().test_name,
            "D. PTERONYSSINUS"
        )
        self.assertEqual(
            reloaded.labtest_set.get().observation_set.get().observation_name,
            "COMMENT"
        )

    def test_update_from_dict_update_observation(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        observations = as_dict["labtest_set"][0]["observation_set"]
        obs = [i for i in observations if i["observation_name"] == "kul"][0]
        obs["observation_value"] = "1.0"
        specimen.update_from_dict(as_dict, user=self.user)
        obs = Observation.objects.filter(observation_name='kul').get()
        self.assertEqual(
            obs.observation_value, "1.0"
        )

    def test_update_from_dict_delete_observation(self):
        specimen = self.create_specimen()
        as_dict = specimen.to_dict(self.user)
        as_dict["labtest_set"][0]["observation_set"] = []
        specimen.update_from_dict(as_dict, user=self.user)
        self.assertFalse(Observation.objects.exists())

    def test_update_from_dict_create_observation(self):
        specimen = self.create_specimen()
        Observation.objects.all().delete()
        as_dict = specimen.to_dict(self.user)
        as_dict["labtest_set"][0]["observation_set"] = [{
            "observation_name": "COMMENT",
        }]
        specimen.update_from_dict(as_dict, user=self.user)
        obs = Observation.objects.filter(test__specimen_id=specimen.id).get()
        self.assertEqual(
            obs.observation_name, "COMMENT"
        )
