import datetime
from opal.core.test import OpalTestCase
from plugins.lab.models import Bloods, BloodResult


class BloodsTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_to_dict(self):
        self.maxDiff = None
        bloods = Bloods(patient=self.patient)
        bloods.blood_date = datetime.date(2020, 9, 28)
        bloods.assayno = "123"
        bloods.store = False
        bloods.save()
        bloods_result = bloods.bloodresult_set.create()
        bloods_result.allergen = "flour"
        bloods_result.precipitin = "+ve"
        bloods_result.save()
        expected = {
            "antigen_date": None,
            "antigen_type": None,
            "assay_date": None,
            "assayno": "123",
            "batches": None,
            "blood_collected": None,
            "blood_date": datetime.date(2020, 9, 28),
            "blood_number": None,
            "blood_taken": None,
            "blood_tm": None,
            "authorised_by": None,
            "bloodresult": [
                {
                    "allergen": "flour",
                    "phadia_test_code": None,
                    "id": bloods_result.id,
                    "igg": None,
                    "iggclass": None,
                    "klass": None,
                    "kul": None,
                    "precipitin": "+ve",
                    "rast": None,
                    "result": None,
                    "rast_score": None,
                    "significant": True
                }
            ],
            'comment': None,
            "consistency_token": "",
            "created": None,
            "created_by_id": None,
            'date_dna_extracted': None,
            'exposure': '',
            'freezer': None,
            "id": bloods.id ,
            "method": None,
            "patient_id": self.patient.id,
            "report_dt": None,
            "report_st": None,
            "room": None,
            "shelf": None,
            "store": False,
            "tray": None,
            "updated": None,
            "updated_by_id": None,
            "vials": None
        }
        result = bloods.to_dict(user=None)
        self.assertEqual(result, expected)

    def test_update_from_dict_create(self):
        update_dict = {
            "exposure": "wheat",
            "bloodresult": [{
                "result": "result"
            }]
        }
        bloods = Bloods(patient=self.patient)
        bloods.update_from_dict(update_dict, self.user)
        bloods_reloaded = Bloods.objects.get()
        self.assertEqual(
            bloods_reloaded.exposure, "wheat"
        )
        self.assertEqual(
            bloods.bloodresult_set.get().result, "result"
        )

    def test_update_from_dict_empty_result(self):
        update_dict = {
            "exposure": "wheat",
        }
        bloods = Bloods(patient=self.patient)
        bloods.update_from_dict(update_dict, self.user)
        bloods_reloaded = Bloods.objects.get()
        self.assertEqual(
            bloods_reloaded.exposure, "wheat"
        )
        self.assertFalse(bloods.bloodresult_set.exists())

    def test_update_from_dict_delete(self):
        bb = Bloods(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb.bloodresult_set.create(result="result")
        bb.update_from_dict({
            "exposure": "wheat",
            "bloodresult": []
        }, self.user)
        bb_reloaded = Bloods.objects.get()
        self.assertEqual(
            bb_reloaded.exposure, "wheat"
        )
        self.assertFalse(
            bb_reloaded.bloodresult_set.exists()
        )

    def test_update_from_dict_update(self):
        bb = Bloods(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb_result = bb.bloodresult_set.create(result="result")
        bb.update_from_dict({
            "exposure": "wheat",
            "bloodresult": [{
                "id": bb_result.id,
                "result": "other result"
            }]
        }, self.user)
        bb_reloaded = Bloods.objects.get()
        self.assertEqual(
            bb_reloaded.exposure, "wheat"
        )
        self.assertEqual(
            bb_reloaded.bloodresult_set.get().result,
            "other result"
        )

    def test_cascade(self):
        bb = Bloods(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb.bloodresult_set.create(result="result")
        bb.delete()
        self.assertFalse(BloodResult.objects.exists())


class BloodResultTestCase(OpalTestCase):
    def setUp(self):
        patient, _ = self.new_patient_and_episode_please()
        bloods = patient.bloods_set.create()
        self.blood_result = bloods.bloodresult_set.create()

    def test_not_significant(self):
        self.assertFalse(self.blood_result.is_significant())

    def test_significant_rast(self):
        self.blood_result.rast = 2.0
        self.assertTrue(self.blood_result.is_significant())

        self.blood_result.rast = 1.99
        self.assertFalse(self.blood_result.is_significant())

    def test_significant_precipitin(self):
        self.blood_result.precipitin = "+ve"
        self.assertTrue(self.blood_result.is_significant())

        self.blood_result.precipitin = "-ve"
        self.assertFalse(self.blood_result.is_significant())

    def test_significant_igg(self):
        self.blood_result.igg = 2
        self.assertTrue(self.blood_result.is_significant())

    def test_significant_kul(self):
        self.blood_result.kul = "< 0.35"
        self.assertFalse(self.blood_result.is_significant())

        self.blood_result.kul = "0.1"
        self.assertFalse(self.blood_result.is_significant())

        self.blood_result.kul = "0.35"
        self.assertTrue(self.blood_result.is_significant())

        self.blood_result.kul = "> 100"
        self.assertTrue(self.blood_result.is_significant())

        self.blood_result.kul = "flawed"
        self.assertFalse(self.blood_result.is_significant())
