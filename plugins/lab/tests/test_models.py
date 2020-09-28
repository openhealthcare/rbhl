import datetime
from opal.core.test import OpalTestCase
from plugins.lab.models import BloodBook


class BloodBookTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_to_dict(self):
        bb = BloodBook(patient=self.patient)
        bb.sample_received = datetime.date(2020, 9, 28)
        bb.assay_number = "123"
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
            "assay_number": "123",
            "blood_number": None,
            "blood_taken": None,
            "bloodbookresult_set": [
                {
                    "allergen": "flour",
                    "antigen_number": None,
                    "id": bb_result.id,
                    "ige_class": None,
                    "igg_class": None,
                    "igg_mg": None,
                    "kul": None,
                    "precipitin": "+ve",
                    "rast": None,
                    "result": None,
                }
            ],
            "consistency_token": "",
            "created": None,
            "created_by_id": None,
            "id": bb.id ,
            "information": "",
            "method": None,
            "patient_id": self.patient.id,
            "reference_number": None,
            "report_date": None,
            "report_submitted": None,
            "sample_received": datetime.date(2020, 9, 28),
            "store": False,
            "updated": None,
            "updated_by_id": None,
        }
        result = bb.to_dict(user=None)
        self.assertEqual(result, expected)

    def test_update_from_dict_create(self):
        update_dict = {
            "antigen_date": None,
            "antigen_type": None,
            "assay_date": None,
            "assay_number": "123",
            "blood_number": None,
            "blood_taken": None,
            "information": "",
            "method": None,
            "patient_id": self.patient.id,
            "reference_number": None,
            "report_date": None,
            "report_submitted": None,
            "sample_received": "28/09/2020",
            "store": False,
        }
        bb = BloodBook(patient=self.patient)
        bb.update_from_dict(update_dict, None)

    def test_update_from_dict_update(self):
        bb = BloodBook(patient=self.patient)
        bb.sample_received = datetime.date(2020, 9, 28)
        bb.assay_number = "123"
        bb.store = False
        bb.save()
        result = bb.bloodbookresult_set.create()
        result.allergen = "alpha amylase"
        result.precipitin = "-ve"
        result.save()
        update_dict = {
            "antigen_date": None,
            "antigen_type": None,
            "assay_date": None,
            "assay_number": "124",
            "blood_number": None,
            "blood_taken": None,
            "bloodbookresult_set": [
                {
                    "allergen": "flour",
                    "antigen_number": None,
                    "id": result.id,
                    "ige_class": None,
                    "igg_class": None,
                    "igg_mg": None,
                    "kul": "< 0.25",
                    "precipitin": None,
                    "rast": None,
                    "result": None,
                }
            ],
            "consistency_token": "",
            "created": None,
            "created_by_id": None,
            "id": bb.id,
            "information": "",
            "method": None,
            "patient_id": self.patient.id,
            "reference_number": None,
            "report_date": None,
            "report_submitted": None,
            "sample_received": "28/09/2020",
            "store": False,
            "updated": None,
            "updated_by_id": None,
        }
        bb.update_from_dict(update_dict, None)
        self.assertEqual(
            bb.assay_number, "124"
        )
        self.assertEqual(
            bb.sample_received, datetime.date(2020, 9, 28)
        )
        result = bb.bloodbookresult_set.get()
        self.assertEqual(
            result.precipitin, None
        )
        self.assertEqual(
            result.allergen, "flour"
        )
        self.assertEqual(
            result.kul, "< 0.25"
        )

    def test_update_from_dict_delete(self):
        bb = BloodBook(patient=self.patient)
        bb.sample_received = datetime.date(2020, 9, 28)
        bb.assay_number = "123"
        bb.store = False
        bb.save()
        result = bb.bloodbookresult_set.create()
        result.allergen = "alpha amylase"
        result.precipitin = "-ve"
        result.save()
        update_dict = {
            "antigen_date": None,
            "antigen_type": None,
            "assay_date": None,
            "assay_number": "124",
            "blood_number": None,
            "blood_taken": None,
            "bloodbookresult_set": [],
            "consistency_token": "",
            "created": None,
            "created_by_id": None,
            "id": bb.id,
            "information": "",
            "method": None,
            "patient_id": self.patient.id,
            "reference_number": None,
            "report_date": None,
            "report_submitted": None,
            "sample_received": "28/09/2020",
            "store": False,
            "updated": None,
            "updated_by_id": None,
        }
        bb.update_from_dict(update_dict, self.user)
        self.assertFalse(bb.bloodbookresult_set.exists())
