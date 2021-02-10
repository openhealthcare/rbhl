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


class Bloods(PagePathway):
    display_name = 'Bloods'
    slug = 'bloods'
    template = "pathway/base/bloods_form_base.html"
    steps = [
        Step(
            models.Bloods,
            base_template="pathway/bloods_form.html",
            step_controller="BloodsStep"
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)
