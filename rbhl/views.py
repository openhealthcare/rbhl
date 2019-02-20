"""
Custom views for Lungs@Work
"""
import json

from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import (
    FormView, TemplateView, RedirectView, ListView
)
from django.contrib.auth import login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from two_factor.views import core as two_factor_core_views
from opal.core import serialization
from opal import models as opal_models
from rbhl.patient_lists import StaticTableList
from plugins.trade import match, trade
from plugins.trade.forms import ImportDataForm


class StaffRequiredMixin(object):
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(*args, **kwargs)


class PeakFlowMatcher(match.Matcher):
    """
    Matcher for data in the Opal portable export format.
    """
    direct_match_field     = 'hospital_number'
    attribute_match_fields = [
        'date_of_birth',
        'first_name',
        'surname',
    ]

    def get_demographic_dict(self):
        return self.data


class ImportView(FormView):
    form_class = ImportDataForm
    template_name = 'import.html'

    def get_success_url(self):
        return '/#/patient/{0}'.format(self.patient.id)

    def form_valid(self, form):
        raw_data = self.request.FILES['data_file'].read()
        data = json.loads(raw_data)

        demographics = data['demographics'][0]
        demographics['date_of_birth'] = serialization.deserialize_date(
            demographics['date_of_birth']
        )

        matcher = PeakFlowMatcher(demographics)

        patient, created = matcher.match_or_create()

        episode = patient.episode_set.get()

        self.patient = patient
        self.episode = episode

        peak_flow_days = data['episodes']['1']['peak_flow_day']

        for day_data in peak_flow_days:
            day_data['date'] = serialization.deserialize_date(
                day_data['date']
            )
            day, created = episode.peakflowday_set.get_or_create(date=day_data['date'])
            for key, value in day_data.items():
                setattr(day, key, value)
            day.save()

        return super(ImportView, self).form_valid(form)


class StaticTableListView(ListView):
    """
    View to render a Static HTML table list
    """
    paginate_by = 50

    def dispatch(self, *args, **kwargs):
        """
        Find the relevant PatientList class and attach it to self.patient_list
        """
        self.patient_list = StaticTableList.get(kwargs['slug'])()
        return super(StaticTableListView, self).dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        return self.patient_list.get_queryset(user=self.request.user)

    def get_template_names(self, *args, **kwargs):
        return self.patient_list.template_name


class FormSearchRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = reverse('search_index')
        return url + '#/?query={}'.format(self.request.GET.get('query', ''))


class TwoFactorRequired(TemplateView):
    template_name = "two_factor/two_factor_required.html"


class OtpSetupRelogin(StaffRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("two-factor-setup")

    def get_user(self):
        return User.objects.filter(is_superuser=False).filter(is_staff=False).get(
            username__iexact=self.kwargs["username"]
        )

    def get(self, request, *args, **kwargs):
        logout(request)
        login(request, self.get_user())
        return super().get(request, *args, **kwargs)


class ChangePasswordCheck(RedirectView):
    def get_redirect_url(self):
        profile, _ = opal_models.UserProfile.objects.get_or_create(
            user=self.request.user
        )
        if profile.force_password_change:
            return reverse('change-password')
        else:
            return reverse('home')


class TwoFactorSetupView(two_factor_core_views.SetupView):
    @property
    def success_url(self):
        return reverse('home')
