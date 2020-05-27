"""
Pathways for the rbhl app
"""
from opal.core.pathway import Step, WizardPathway, PagePathway
from plugins.add_patient_step import FindPatientStep

from rbhl import models


class NewReferral(WizardPathway):
    display_name = 'New referral'
    icon = 'fa-plus'
    slug = 'new_referral'
    finish_button_text = "Create new referral"
    finish_button_icon = None
    template = "pathway/base/rbhl_referral_base.html"
    steps = [
        FindPatientStep(
            base_template="pathway/steps/step_base_without_display_name.html"
        ),
        Step(
            display_name="Referral details",
            template="pathway/new_referral.html",
            base_template="pathway/steps/step_base_without_display_name.html"
        )
    ]

    def save(self, *args, **kwargs):
        patient, episode = super().save(*args, **kwargs)
        clinical_log = episode.cliniclog_set.get()
        clinical_log.active = True
        clinical_log.save()
        return patient, episode


class PeakFlowStep(Step):
    """
    The peak flow step assumes an arbitrary key of `trial_num`
    that is the trial num for the peak flow days we are looking at.

    We delete all ids that are not in the current peak flow set.
    """
    step_controller = "PeakFlowStep"
    template = "pathway/steps/peak_flow_step.html"
    base_template = "pathway/steps/peak_flow_step_base.html"
    model = models.PeakFlowDay
    display_name = "Peak Flow Day"

    def pre_save(self, data, user, patient=None, episode=None):
        """
        The Peak flow step does not look at all an episodes peak flows
        just those related to a specific trial number.

        So when we are looking at which dates have been deleted we need
        the qs in question to be limitted by that trial number.
        """
        trial_num = int(data.pop("trial_num")[0])
        qs = episode.peakflowday_set.all()
        existing_ids = [i.get("id") for i in data[
            models.PeakFlowDay.get_api_name()
        ]]
        existing_ids = [i for i in existing_ids if i]
        to_remove = qs.exclude(
            id__in=existing_ids
        ).filter(
            trial_num=trial_num
        )
        to_remove.delete()


class PeakFlowDayPathway(PagePathway):
    """
    The peak flow pathway allows you to enter data for a specific
    trial which is added as a get parameter and passed through
    to the data on post.
    """
    display_name = 'Peak Flow'
    slug = 'peak_flow_day'
    template = "pathway/base/rbhl_flow_pathway_base.html"
    steps = [
        PeakFlowStep(),
    ]


class PeakFlowGraphFullPage(PagePathway):
    display_name = 'Peak Graph View'
    slug = 'peak_graph_view'
    template = "pathway/base/rbhl_graph_base.html"
    steps = [
        models.Demographics,
    ]


class SkinPrickTest(PagePathway):
    display_name = "Skin Prick Test"
    slug = "skin_prick_test"
    template = "pathway/base/rbhl_skin_prick_test_base.html"
    steps = [
        Step(
            models.SkinPrickTest,
            base_template="pathway/steps/skin_prick_test_form.html",
            step_controller="SkinPrickTestController",
        )
    ]

    def redirect_url(self, user=None, patient=None, episode=None):
        return "/#/patient/{0}/investigations".format(patient.id)
