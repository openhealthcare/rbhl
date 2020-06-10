from opal.core.pathway import Step, PagePathway
from plugins.lab import models


class SkinPrickTest(PagePathway):
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
