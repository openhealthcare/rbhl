"""
Pathways for the rbhl app
"""
from opal.core.pathway import PagePathway
from plugins.add_patient_step import FindPatientStep

from rbhl import models


class NewReferral(PagePathway):
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
    ]

    def save(self, *args, **kwargs):
        patient, episode = super().save(*args, **kwargs)
        clinical_log = episode.cliniclog_set.get()
        clinical_log.active = True
        clinical_log.save()
        return patient, episode


class PeakFlowDayPathway(PagePathway):
    display_name = 'Peak Flow Day'
    slug = 'peak_flow_day'
    steps = [
        models.PeakFlowDay
    ]
