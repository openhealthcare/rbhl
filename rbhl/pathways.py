"""
Pathways for the rbhl app
"""
from opal.core.pathway import Step, WizardPathway, PagePathway

from rbhl import models

class NewReferral(WizardPathway):
    display_name = 'New Referral'
    icon = 'fa-plus'
    slug = 'new_referral'
    template = "pathway/base/rbhl_page_pathway_base.html"
    steps = [
        Step(
            template="pathway/referral_form.html",
            display_name="Shut up Pathway",
            icon="fa fa-user",
            base_template="pathway/steps/step_base_without_display_name.html"
        ),
    ]


class PeakFlowDayPathway(PagePathway):
    display_name = 'Peak Flow Day'
    slug = 'peak_flow_day'
    steps = [
        models.PeakFlowDay
    ]
