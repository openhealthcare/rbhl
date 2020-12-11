import datetime
from opal.core.test import OpalTestCase
from legacy.models import BloodBook, BloodBookResult


class BloodBookTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_to_dict(self):
        self.maxDiff = None
        bb = BloodBook(patient=self.patient)
        bb.blood_date = datetime.date(2020, 9, 28)
        bb.assayno = "123"
        bb.store = False
        bb.save()
        bb_result = bb.bloodbookresult_set.create()
        bb_result.allergen = "flour"
        bb_result.precipitin = "+ve"
        bb_result.save()
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
            "bloodbookresult": [
                {
                    "allergen": "flour",
                    "phadia_test_code": None,
                    "id": bb_result.id,
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
            "id": bb.id ,
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
        result = bb.to_dict(user=None)
        self.assertEqual(result, expected)

    def test_update_from_dict_create(self):
        update_dict = {
            "exposure": "wheat",
            "bloodbookresult": [{
                "result": "result"
            }]
        }
        bb = BloodBook(patient=self.patient)
        bb.update_from_dict(update_dict, self.user)
        bb_reloaded = BloodBook.objects.get()
        self.assertEqual(
            bb_reloaded.exposure, "wheat"
        )
        self.assertEqual(
            bb_reloaded.bloodbookresult_set.get().result, "result"
        )

    def test_update_from_dict_delete(self):
        bb = BloodBook(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb.bloodbookresult_set.create(result="result")
        bb.update_from_dict({
            "exposure": "wheat",
            "bloodbookresult": []
        }, self.user)
        bb_reloaded = BloodBook.objects.get()
        self.assertEqual(
            bb_reloaded.exposure, "wheat"
        )
        self.assertFalse(
            bb_reloaded.bloodbookresult_set.exists()
        )

    def test_update_from_dict_update(self):
        bb = BloodBook(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb_result = bb.bloodbookresult_set.create(result="result")
        bb.update_from_dict({
            "exposure": "wheat",
            "bloodbookresult": [{
                "id": bb_result.id,
                "result": "other result"
            }]
        }, self.user)
        bb_reloaded = BloodBook.objects.get()
        self.assertEqual(
            bb_reloaded.exposure, "wheat"
        )
        self.assertEqual(
            bb_reloaded.bloodbookresult_set.get().result,
            "other result"
        )

    def test_cascade(self):
        bb = BloodBook(patient=self.patient)
        bb.exposure = "wheat"
        bb.save()
        bb.bloodbookresult_set.create(result="result")
        bb.delete()
        self.assertFalse(BloodBookResult.objects.exists())


class BloodBookResultTestCase(OpalTestCase):
    def setUp(self):
        patient, _ = self.new_patient_and_episode_please()
        bb = patient.bloodbook_set.create()
        self.bb_result = bb.bloodbookresult_set.create()

    def test_not_significant(self):
        self.assertFalse(self.bb_result.is_significant())

    def test_significant_rast(self):
        self.bb_result.rast = 2.0
        self.assertTrue(self.bb_result.is_significant())

        self.bb_result.rast = 1.99
        self.assertFalse(self.bb_result.is_significant())

    def test_significant_precipitin(self):
        self.bb_result.precipitin = "+ve"
        self.assertTrue(self.bb_result.is_significant())

        self.bb_result.precipitin = "-ve"
        self.assertFalse(self.bb_result.is_significant())

    def test_significant_igg(self):
        self.bb_result.igg = 2
        self.assertTrue(self.bb_result.is_significant())

    def test_significant_kul(self):
        self.bb_result.kul = "< 0.35"
        self.assertFalse(self.bb_result.is_significant())

        self.bb_result.kul = "0.1"
        self.assertFalse(self.bb_result.is_significant())

        self.bb_result.kul = "0.35"
        self.assertTrue(self.bb_result.is_significant())

        self.bb_result.kul = "> 100"
        self.assertTrue(self.bb_result.is_significant())

        self.bb_result.kul = "flawed"
        self.assertFalse(self.bb_result.is_significant())
