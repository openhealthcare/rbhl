from opal.core.pathway import Step, PagePathway
from plugins.lab import models


class SkinPrickTest(PagePathway):
    icon = 'fa-crosshairs'
    display_name = "Skin Prick Test"
    slug = "skin_prick_test"
    template = "pathway/skin_prick_test_base.html"
    steps = [
        Step(
            models.SkinPrickTest,
            base_template="pathway/skin_prick_test_form.html",
            step_controller="SkinPrickTestController",
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)


class BloodBook(PagePathway):
    display_name = 'Blood book'
    slug = 'blood_book'
    template = "pathway/base/rbhl_pathway_base.html"
    steps = [
        Step(
            models.BloodBook,
            base_template="pathway/blood_book_form.html",
            step_controller="BloodBookStep"
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)
