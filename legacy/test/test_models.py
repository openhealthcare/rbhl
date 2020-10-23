import datetime
from opal.core.test import OpalTestCase
from legacy.models import BloodBook


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
            "bloodbookresult_set": [
                {
                    "allergen": "flour",
                    "antigenno": None,
                    "id": bb_result.id,
                    "igg": None,
                    "iggclass": None,
                    "klass": None,
                    "kul": None,
                    "precipitin": "+ve",
                    "rast": None,
                    "result": None,
                }
            ],
            'comment': None,
            "consistency_token": "",
            "created": None,
            "created_by_id": None,
            'date_dna_extracted': None,
            'employer': None,
            'exposure': '',
            'freezer': None,
            "id": bb.id ,
            "information": None,
            "method": None,
            "oh_provider": None,
            "patient_id": self.patient.id,
            "reference_number": None,
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
