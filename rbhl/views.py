"""
Custom views for Lungs@Work
"""
import json
import datetime
import statistics
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView, RedirectView, ListView
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from two_factor.views import core as two_factor_core_views
from opal.core import serialization
from opal.models import Episode
from opal import models as opal_models
from plugins.trade import match
from plugins.trade.forms import ImportDataForm
from plugins.lab.models import SkinPrickTest
from rbhl.models import SetUpTwoFactor, Referral, EmploymentCategory, GeographicalArea


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
            day, created = episode.peakflowday_set.get_or_create(
                date=day_data['date']
            )
            for key, value in day_data.items():
                setattr(day, key, value)
            day.save()

        return super(ImportView, self).form_valid(form)


class BasePatientList(ListView):
    queryset = Episode.objects.filter(cliniclog__active=True).prefetch_related(
        "cliniclog_set"
    ).prefetch_related(
        "patient__demographics_set"
    )

    def get_ordering(self):
        options = {
            "hospital_number": "patient__demographics__hospital_number",
            "name": "patient__demographics__first_name",
            "days_since_first_attended": "cliniclog__clinic_date",
            "seen_by": "cliniclog__seen_by"
        }
        order_param = self.request.GET.get(
            "order", "days_since_first_attended")

        if order_param.startswith("-"):
            order_param = order_param[1:]
            return "-{}".format(options[order_param])
        else:
            return options[order_param]


class ActivePatientList(BasePatientList):
    """
    The active patients as per the RBHL 18 week database
    """
    template_name = 'patient_lists/active_patients.html'


class SeenByMeList(BasePatientList):
    template_name = "patient_lists/seen_by_me.html"

    def initials(self):
        first_name = self.request.user.first_name or " "
        surname = self.request.user.last_name or " "
        return "{}{}".format(first_name[0], surname[0]).strip().upper()

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        initials = self.initials()
        if initials:
            return qs.filter(cliniclog__seen_by__icontains=self.initials())
        return qs.none()

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["initials"] = self.initials()
        return ctx


class FormSearchRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        url = reverse('search_index')
        return url + '#/?query={}'.format(self.request.GET.get('query', ''))


class TwoFactorRequired(TemplateView):
    template_name = "two_factor/two_factor_required.html"


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
        return reverse('change-password-check')

    def dispatch(self, request, *args, **kwargs):
        if not SetUpTwoFactor.allowed(request.user):
            logout(request)
            url = reverse("two-factor-required")
            HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)


class AbstractClinicActivity(TemplateView):
    # The fields that appear on the in the table
    PAGE_FIELDS = [
        "Name",
        "Referral",
        "First appointment",
        "Referral",
        # "Diagnosis date",
        "Diagnosis",
        "Seen by",
        "Peak flow",
        "Bloods",
        "General SPT",
        "Specific SPT"
    ]

    def menu_dates(self):
        current_year = datetime.date.today().year
        today = datetime.date.today()
        if today.month < 10:
            start_year = 1
        else:
            start_year = 0
        result = []
        for i in range(start_year, 5 + start_year):
            year = current_year - i
            result.append(self.get_date_range(year))
        result.reverse()
        return result

    def get_date_range(self, start_year):
        """
        Returns a date range of what we are covering
        from october of the start year to end of september
        the next year or the current date depending what's greater
        """
        start_date = datetime.date(start_year, 10, 1)
        end_date = datetime.date(start_year + 1, 9, 30)
        end_date = min(datetime.date.today(), end_date)
        return start_date, end_date

    @cached_property
    def date_range(self):
        """
        The date range we are covering.
        returns [start_date, end_date] inclusive
        """
        year = int(self.kwargs["year"])
        return self.get_date_range(year)

    @cached_property
    def referral_id_to_episode_id(self):
        referrals = Referral.objects.filter(
            ocld=True,
            date_of_referral__gte=self.date_range[0],
            date_of_referral__lte=self.date_range[1],
        ).values_list("id", "episode_id")
        return dict(referrals)

    @cached_property
    def gender(self):
        return dict(
            opal_models.Gender.objects.values_list('id', 'name')
        )

    @cached_property
    def employment_category(self):
        return dict(
            EmploymentCategory.objects.values_list('id', 'name')
        )

    @cached_property
    def geographics_area(self):
        return dict(
            GeographicalArea.objects.values_list('id', 'name')
        )

    def get_queryset(self):
        return opal_models.Episode.objects.filter(
            id__in=self.referral_id_to_episode_id.values()
        ).prefetch_related(
            "cliniclog_set",
            "referral_set",
            "diagnosis_set",
            "employment_set",
            "asthmadetails_set",
            "rhinitisdetails_set",
            "peakflowday_set",
            "patient__demographics_set",
            "patient__skinpricktest_set",
            "patient__bloods_set__bloodresult_set"
        )

    def get_display_name(self, demographics, date_of_referral):
        name = demographics.name
        gender = self.gender.get(demographics.sex_fk_id, demographics.sex_ft)
        sex = ""
        if gender:
            sex = gender[0]
        age = demographics.get_age(date_of_referral) or ""
        if age or sex:
            return f"{name} ({sex}{age})"
        return name

    def get_diagnosis(self, episode):
        result = []
        diagnoses = episode.diagnosis_set.all()
        rhinitis_details = episode.rhinitisdetails_set.all()
        asthma_details = episode.asthmadetails_set.all()

        for diagnosis in diagnoses:
            if diagnosis.condition == diagnosis.ASTHMA:
                asthma_details = [i for i in asthma_details if i.date == diagnosis.date]
                if asthma_details and asthma_details[0].trigger:
                    result.append(
                        f"{diagnosis.condition} ({asthma_details[0].trigger})"
                    )
                else:
                    result.append(diagnosis.condition)
            elif diagnosis.condition == diagnosis.RHINITIS:
                rhinitis_details = [
                    i for i in rhinitis_details if i.date == diagnosis.date
                ]
                if rhinitis_details and rhinitis_details[0].trigger:
                    result.append(
                        f"{diagnosis.condition} ({rhinitis_details[0].trigger})"
                    )
                else:
                    result.append(diagnosis.condition)
            else:
                if diagnosis.occupational:
                    result.append(f"{diagnosis.condition} (occupational)")
                else:
                    result.append(diagnosis.condition)
        return result

    def get_peak_flow(self, episode, clinic_log):
        peak_flow_days = episode.peakflowday_set.all()
        result = "Not requested"
        if clinic_log.peak_flow:
            result = "Not received"
        if peak_flow_days:
            result = "Received"
        return result

    def get_bloods(self, episode, referral):
        bloods = []

        # pick up the prefetch related bloods set from the episode qs
        for blood in episode.patient.bloods_set.all():
            if blood.referral_id == referral.id:
                bloods.append(blood)
        test_types = []
        stored = False
        for blood in bloods:
            if blood.store:
                stored = True

            for blood_result in blood.bloodresult_set.all():
                kul = blood_result.kul is not None
                rast = blood_result.rast is not None
                rast_score = blood_result.rast_score is not None
                if kul is not None:
                    antigen_type = ""
                    if blood.antigen_type:
                        antigen_type = blood.antigen_type.title()

                    test_types.append(
                        f"{antigen_type} IgE".strip()
                    )
                elif rast or rast_score:
                    test_types.append("RAST or RAST Score")
                elif blood_result.precipitin:
                    test_types.append("Precipitin")
        test_types = sorted(list(set([i for i in test_types if i])))
        return {
            "Bloods": test_types,
            "Bloods stored": stored
        }

    def get_skin_prick_tests(self, episode):
        spts = episode.patient.skinpricktest_set.all()
        substances = [i.substance for i in spts]
        routines = []
        nonroutines = []
        for substance in substances:
            if substance in SkinPrickTest.ROUTINE_TESTS:
                routines.append(substance)
            else:
                nonroutines.append(substance)

        routine = False
        if len(set(routines)) == len(SkinPrickTest.ROUTINE_TESTS):
            routine = True

        return {
            "General SPT": routine,
            "Specific SPT": sorted(list(nonroutines))
        }

    def get_row(self, episode, referral):
        demographics = episode.patient.demographics_set.all()[0]
        date_of_referral = referral.date_of_referral
        clinic_log = episode.cliniclog_set.all()[0]
        diagnosis = episode.diagnosis_set.all()
        days_to_appointment = None
        gender = self.gender.get(demographics.sex_fk_id, demographics.sex_ft)
        geographical_area = self.geographics_area.get(
            referral.geographical_area_fk_id, referral.geographical_area_ft
        )

        if clinic_log.clinic_date:
            if clinic_log.clinic_date >= referral.date_of_referral:
                days_to_appointment = clinic_log.clinic_date - referral.date_of_referral
                days_to_appointment = days_to_appointment.days

        days_to_diagnosis = None
        diagnosis_dates = sorted([
            i.date for i in diagnosis if i.date and i.date >= referral.date_of_referral
        ])
        diagnosis_date = None
        if diagnosis_dates:
            diagnosis_date = diagnosis_dates[0]
        if referral.date_of_referral and diagnosis_date:
            days_to_diagnosis = diagnosis_date - referral.date_of_referral
            days_to_diagnosis = days_to_diagnosis.days
        employments = list(episode.employment_set.all())
        employment_category = ""
        if employments:
            # this needs work
            employment_category = self.employment_category.get(
                employments[-1].employment_category_fk_id,
                employments[-1].employment_category_ft
            )
        row = {
            "Name": self.get_display_name(demographics, date_of_referral),
            "First name": demographics.first_name,
            "Surname": demographics.surname,
            "Age at referral": demographics.get_age(date_of_referral),
            "Sex": gender,
            "Referral": referral.date_of_referral,
            "OCLD": referral.ocld,
            "First appointment": clinic_log.clinic_date,
            "Diagnosis date": diagnosis_date,
            "Referral time to first appointment": days_to_appointment,
            "Referral time to diagnosis": days_to_diagnosis,
            "Geographic area": geographical_area,
            "Employment category": employment_category,
            "Seen by": clinic_log.seen_by,
            "Source of referral": referral.referral_source,
            "Peak flow": self.get_peak_flow(episode, clinic_log),
            "Diagnosis": self.get_diagnosis(episode),
            "Diagnosis outcome": clinic_log.diagnosis_outcome,
            "Link": episode.get_absolute_url()
        }
        row.update(self.get_bloods(episode, referral))
        row.update(self.get_skin_prick_tests(episode))
        return row

    def get_rows(self, *args, **kwargs):
        rows = []
        qs = self.get_queryset()
        for episode in qs:
            for referral in episode.referral_set.all():
                if referral.id in self.referral_id_to_episode_id:
                    rows.append(self.get_row(episode, referral))
        rows = sorted(rows, key=lambda x: x["Referral"])
        return rows


class ClinicActivityOverview(AbstractClinicActivity):
    template_name = "stats/clinic_activity_overview.html"

    def get_head_lines(self, rows):
        total = len(rows)
        k = "Diagnosis outcome"
        diagnosed = len(
            [i for i in rows if i[k] and i[k] == "Known"]
        )
        ref_time = "Referral time to diagnosis"
        mean_days_to_diangosis = statistics.mean(
            [i[ref_time] for i in rows if i[ref_time] is not None]
        )
        return {
            "Referrals": total,
            "% diagnosed": "{:.1f}".format((diagnosed/total) * 100),
            "Mean days to diagnosis": "{:.1f}".format(mean_days_to_diangosis)
        }

    def get_flow(self, rows):
        day_ranges = [i for i in range(0, 200, 20)]
        to_appointment_date = [0 for i in day_ranges]
        to_diagnosis_date = [0 for i in day_ranges]
        for row in rows:
            to_appointment = row["Referral time to first appointment"]
            if to_appointment is not None:
                idx = min(int(to_appointment/20), len(day_ranges)-1)
                to_appointment_date[idx] += 1
            to_diagnosis = row["Referral time to diagnosis"]
            if to_diagnosis is not None:
                idx = min(int(to_diagnosis/20), len(day_ranges)-1)
                to_diagnosis_date[idx] += 1
        x_axis = []
        for idx, i in enumerate(day_ranges):
            if idx + 1 == len(day_ranges):
                x_axis.append(f"{i} +")
            else:
                x_axis.append(f"{i} - {day_ranges[idx + 1]}")
        return {
            "x": x_axis,
            "vals": [
                ["Days to first appointment offered"] + to_appointment_date,
                ["Days to diagnosis"] + to_diagnosis_date
            ]
        }

    def get_aggregates(self):
        rows = self.get_rows()
        result = {}
        result["head_lines"] = self.get_head_lines(rows)
        result["patient_flow"] = self.get_flow(rows)
        return result

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["aggregates"] = self.get_aggregates()
        return ctx


class ClinicActivityPatients(AbstractClinicActivity):
    template_name = "stats/clinic_activity_patients.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["rows"] = self.get_rows(*args, **kwargs)
        return ctx
