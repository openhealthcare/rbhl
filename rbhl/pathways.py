"""
Pathways for the rbhl app
"""
from opal.core.pathway import Step, WizardPathway, PagePathway
from add_patient_step import FindPatientStep

from rbhl import models


class NewReferral(WizardPathway):
    display_name = 'New referral'
    icon = 'fa-plus'
    slug = 'new_referral'
    finish_button_text = "Create new referral"
    finish_button_icon = None
    template = "pathway/base/rbhl_page_pathway_base.html"
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


class PeakFlowDayPathway(PagePathway):
    display_name = 'Peak Flow Day'
    slug = 'peak_flow_day'
    steps = [
        models.PeakFlowDay
    ]
