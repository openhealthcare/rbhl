"""
Pathways for the rbhl app
"""
from opal.core.pathway import Step, WizardPathway, PagePathway

from rbhl import models

class AddPatient(WizardPathway):
    display_name = 'Add Patient'
    icon = 'fa-plus'
    slug = 'add_patient'
    steps = [
        Step(
            template="pathway/add_form.html",
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
