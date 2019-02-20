"""
Defining Opal PatientLists
"""
import datetime
from functools import partial

from django.urls import reverse
from opal import core
from opal.models import Episode
from opal.utils import AbstractBase

from rbhl import models

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
            letter=None).exclude(
                peakflowday=None
            ).order_by('-cliniclog__clinic_date')[:20]


class StaticTableList(core.patient_lists.PatientList, AbstractBase):
    """
    A patient list which is entirely rendered on the server without
    Javascripts.
    """
    icon = 'fa-table'

    @classmethod
    def get_absolute_url(klass):
        """
        Return the absolute URL for this list
        """
        return reverse('static-list', kwargs={'slug': klass.get_slug()})


class ActivePatients(StaticTableList):
    """
    As per the RBHL 18 week database
    """
    template_name = 'patient_lists/active_patients.html'
    display_name  = 'Active patients'

    def get_queryset(self):
        """
        Only those patients who are active
        """
        return Episode.objects.filter(cliniclog__active=True).order_by("cliniclog__clinic_date")


class MinePatientList(StaticTableList):
    template_name = 'patient_lists/active_patients.html'
    display_name = 'My patients'

    def extract_initials(self, sn):
        return [
            i.strip()[0] for i in sn.split(" ") if i.strip()
        ]

    def get_initials(self, user):
        initials = []

        if user.first_name:
            initials.extend(self.extract_initials(user.first_name))
        if user.last_name:
            initials.extend(self.extract_initials(user.last_name))
        return "".join(initials)

    def get_queryset(self, user=None):
        """
        Only those patients who are active
        """
        initials = self.get_initials(user)

        if not initials:
            return Episode.objects.none()

        return Episode.objects.filter(
            cliniclog__seen_by__icontains=initials
        ).order_by("-cliniclog__clinic_date")
