"""
Defining Opal PatientLists
"""
from functools import partial
from opal import core
from opal.models import Episode


Column = partial(
    core.patient_lists.Column,
    limit=None,
    singleton=True,
    detail_template_path=None
)

ReferralSummary = Column(
    name="referral",
    title="Referral",
    template_path='columns/referral_summary.html'

)
Appointment = Column(
    name="appointment",
    title="Appointment",
    template_path="columns/appointment.html"
)

DemographicsColumn = Column(
    name="demographics",
    title="Demographics",
    template_path="columns/demographics.html"
)


class WithLetter(core.patient_lists.PatientList):
    icon = 'fa-table'
    display_name = 'Some Patients'
    template_name = 'patient_lists/layouts/table_list.html'
    comparator_service = 'ClinicDateComparator'

    schema = [
        DemographicsColumn,
        ReferralSummary,
        Appointment
    ]

    def get_queryset(self, **kwargs):
        return Episode.objects.exclude(
            letter=None
        ).exclude(
            peakflowday=None
        ).order_by(
            '-cliniclog__clinic_date'
        )[:20]
