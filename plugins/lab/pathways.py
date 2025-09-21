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


class CTChestPathway(PagePathway):
    """
    As it's bafflingly hard to do non-global form defaults, we create
    this entire pathway to write the string 'CT chest scan' in the field `test`.

    Better implementation suggestions definitely welcome.
    """

    icon         = 'fa-crosshairs'
    display_name = 'CT Chest'
    slug         = 'ct-chest'
    template     = 'pathway/other_investigations_base.html'
    steps        = [
        Step(
            models.OtherInvestigations,
            base_template='pathway/ct_chest_form.html',
            step_controller="CTChestPathwayStepController"
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)
