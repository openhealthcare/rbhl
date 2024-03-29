"""
Custom views for Lungs@Work
"""
import json
import datetime
from collections import defaultdict
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
from opal.models import UserProfile
from plugins.trade import match
from plugins.trade.forms import ImportDataForm
from plugins.lab.models import SkinPrickTest
from plugins.lab.views import zip_file_to_response, ZipCsvWriter
from rbhl.models import (
    SetUpTwoFactor, Referral, EmploymentCategory, GeographicalArea, Fact
)
from rbhl import constants


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
        if not initials:
            return qs.none()
        user = self.request.user
        if UserProfile.objects.filter(
            user=user,
            roles__name=constants.DOCTOR_ROLE
        ).exists():
            return qs.filter(cliniclog__seen_by__icontains=initials)
        else:
            return qs.filter(cliniclog__cns__icontains=initials)

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
            cliniclog__clinic_date__gte=self.date_range[0],
            cliniclog__clinic_date__lte=self.date_range[1],
            referral__occld=True
        ).distinct().prefetch_related(
            "cliniclog_set",
            "referral_set",
            "diagnosis_set",
            "employment_set",
            "asthmadetails_set",
            "rhinitisdetails_set",
            "peakflowday_set",
            "patient__demographics_set",
            "patient__skinpricktest_set",
            "patient__bloods_set__bloodresult_set",
            "patient__spirometry_set"
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
        specific_diagnosis = []
        diagnosis_category = []
        diagnoses = episode.diagnosis_set.all()
        rhinitis_details = episode.rhinitisdetails_set.all()
        asthma_details = episode.asthmadetails_set.all()
        occupational = 0
        total = 0

        for diagnosis in diagnoses:
            total += 1
            diagnosis_category.append(diagnosis.category)
            if diagnosis.condition == diagnosis.ASTHMA:
                asthma_details = [i for i in asthma_details if i.date == diagnosis.date]
                if asthma_details and asthma_details[0].trigger:
                    trigger = asthma_details[0].trigger
                    if not trigger == asthma_details[0].NON_OCCUPATIONAL:
                        occupational += 1
                    specific_diagnosis.append(
                        f"{diagnosis.condition} ({trigger})"
                    )
                else:
                    specific_diagnosis.append(diagnosis.condition)
            elif diagnosis.condition == diagnosis.RHINITIS:
                rhinitis_details = [
                    i for i in rhinitis_details if i.date == diagnosis.date
                ]
                if rhinitis_details and rhinitis_details[0].trigger:
                    trigger = rhinitis_details[0].trigger
                    if not trigger == rhinitis_details[0].NON_OCCUPATIONAL:
                        occupational += 1
                    specific_diagnosis.append(
                        f"{diagnosis.condition} ({trigger})"
                    )
                else:
                    specific_diagnosis.append(diagnosis.condition)
            else:
                if diagnosis.occupational:
                    occupational += 1
                    specific_diagnosis.append(f"{diagnosis.condition} (occupational)")
                else:
                    specific_diagnosis.append(diagnosis.condition or diagnosis.category)
        return {
            "Diagnosis": specific_diagnosis,
            "Diagnosis category": diagnosis_category,
            "Occupational diagnosis": f"{occupational}/{total}"
        }

    def get_peak_flow(self, episode, clinic_log):
        peak_flow_days = episode.peakflowday_set.all()
        result = "Not requested"
        if clinic_log.peak_flow_requested:
            result = "Not returned"
        if peak_flow_days:
            result = "Returned"
        return result

    def get_bloods(self, episode, referral):
        bloods = []

        # pick up the prefetch related bloods set from the episode qs
        if referral:
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

    def get_spirometry(self, episode):
        spirometry = episode.patient.spirometry_set.all()
        external_spirometry = episode.cliniclog_set.all()[0].external_spirometry_done

        if spirometry and external_spirometry:
            return "External and RBHL"
        elif spirometry:
            return "RBHL"
        elif external_spirometry:
            return "External"
        return "Not done"

    def get_row(self, episode, referral):
        date_of_referral = None
        if referral:
            date_of_referral = referral.date_of_referral
            referral_source = referral.referral_source
            referral_disease = referral.referral_disease

        demographics = episode.patient.demographics_set.all()[0]
        clinic_log = episode.cliniclog_set.all()[0]
        diagnosis = episode.diagnosis_set.all()
        days_to_appointment = None
        gender = self.gender.get(demographics.sex_fk_id, demographics.sex_ft)
        geographical_area = self.geographics_area.get(
            referral.geographical_area_fk_id, referral.geographical_area_ft
        )

        if clinic_log.clinic_date and date_of_referral:
            if clinic_log.clinic_date >= date_of_referral:
                days_to_appointment = clinic_log.clinic_date - date_of_referral
                days_to_appointment = days_to_appointment.days

        days_to_diagnosis = None
        diagnosis_date = None
        if date_of_referral:
            diagnosis_dates = sorted([
                i.date for i in diagnosis if i.date and i.date >= date_of_referral
            ])
            if diagnosis_dates:
                diagnosis_date = diagnosis_dates[0]
            if date_of_referral and diagnosis_date:
                days_to_diagnosis = diagnosis_date - date_of_referral
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
            "Referral": date_of_referral,
            "First appointment": clinic_log.clinic_date,
            "Diagnosis date": diagnosis_date,
            "Days from referral to first appointment offered": days_to_appointment,
            "Days from referral to diagnosis": days_to_diagnosis,
            "Geographic area": geographical_area,
            "Employment category": employment_category,
            "Seen by": clinic_log.seen_by,
            "Source of referral": referral_source,
            "Referral disease": referral_disease,
            "Peak flow": self.get_peak_flow(episode, clinic_log),
            "Spirometry": self.get_spirometry(episode),
            "Diagnosis outcome": clinic_log.diagnosis_outcome or "No outcome",
            "Link": episode.get_absolute_url()
        }
        row.update(self.get_bloods(episode, referral))
        row.update(self.get_skin_prick_tests(episode))
        row.update(self.get_diagnosis(episode))
        return row

    def get_rows(self, *args, **kwargs):
        rows = []
        qs = self.get_queryset()
        seen = set()
        for episode in qs:
            if episode.id in seen:
                continue
            referral = Referral.get_recent_referral_for_episode(episode)
            rows.append(self.get_row(episode, referral))
        rows = sorted(rows, key=lambda x: x["First appointment"])
        return rows

    def post(self, *args, **kwargs):
        title = f"clinic_activity_{self.kwargs['year']}"
        zip_file_name = f"{title}.zip"
        rows = self.get_rows()
        for row in rows:
            scheme = self.request.scheme
            host = self.request.get_host()
            row["Link"] = f"{scheme}://{host}{row['Link']}"
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = ", ".join(v)
        with ZipCsvWriter(zip_file_name) as zf:
            zf.write_csv(f"{title}.csv", rows)
        return zip_file_to_response(zf.name)


class ClinicActivityOverview(AbstractClinicActivity):
    template_name = "stats/clinic_activity_overview.html"

    def get_head_lines(self, rows):
        total = len(rows)
        k = "Diagnosis outcome"
        diagnosed = len(
            [i for i in rows if i[k] and i[k] == "Known"]
        )

        mean_patients_per_year = Fact.objects.filter(
            label=Fact.MEAN_CLINIC_PATIENTS_PER_YEAR
        ).order_by("-when").first().val()

        mean_known_diagnosis = Fact.objects.filter(
            label=Fact.FIVE_YEAR_MEAN_KNOWN_DIAGNOSIS
        ).order_by("-when").first()

        if mean_known_diagnosis:
            mean_known_diagnosis = f"{mean_known_diagnosis.val()}%"

        diagnosis_percent = f"{round((diagnosed/total) * 100)}%"
        return (
            ("Patients", total, mean_patients_per_year),
            ("Diagnosed", diagnosis_percent, mean_known_diagnosis),
        )

    def get_flow(self, rows):
        day_ranges = [i for i in range(0, 200, 20)]
        to_appointment_date = [0 for i in day_ranges]
        to_diagnosis_date = [0 for i in day_ranges]
        for row in rows:
            to_appointment = row["Days from referral to first appointment offered"]
            if to_appointment is not None:
                idx = min(int(to_appointment/20), len(day_ranges)-1)
                to_appointment_date[idx] += 1
            to_diagnosis = row["Days from referral to diagnosis"]
            if to_diagnosis is not None:
                idx = min(int(to_diagnosis/20), len(day_ranges)-1)
                to_diagnosis_date[idx] += 1
        x_axis = []
        for idx, i in enumerate(day_ranges):
            if idx + 1 == len(day_ranges):
                x_axis.append(f"{i} +")
            else:
                x_axis.append(f"{i} - {day_ranges[idx + 1]}")
        v1 = ["Days from referral to first appointment offered"] + to_appointment_date
        v2 = ["Days from referral to diagnosis"] + to_diagnosis_date
        no_referral = len([i for i in rows if not i["Referral"]])
        return {
            "x": x_axis,
            "vals": [v1, v2],
            "additional_table_rows": [['No referral date', no_referral]]
        }

    def get_demographics(self, rows):
        age_ranges = [i for i in range(0, 100, 10)]
        male_age = [0 for i in age_ranges]
        female_age = [0 for i in age_ranges]
        male_count = 0
        female_count = 0
        for row in rows:
            age = row["Age at referral"]
            if age is None:
                continue
            idx = min(int(age/10), len(age_ranges)-1)
            if row["Sex"].lower() == "male":
                male_age[idx] += 1
                male_count += 1
            if row["Sex"].lower() == "female":
                female_age[idx] += 1
                female_count += 1
        x_axis = []
        for idx, i in enumerate(age_ranges):
            if idx + 1 == len(age_ranges):
                x_axis.append(f"{i} +")
            else:
                x_axis.append(f"{i} - {age_ranges[idx + 1]}")
        male_percent = "{:.1f}".format(male_count/len(rows) * 100)
        female_percent = "{:.1f}".format(female_count/len(rows) * 100)
        return {
            "x": x_axis,
            "vals": [
                [f"Male {male_percent}%"] + male_age,
                [f"Female {female_percent}%"] + female_age
            ]
        }

    def get_referral(self, rows):
        source_of_referral = defaultdict(int)
        geographic_area = defaultdict(int)
        referral_disease = defaultdict(int)
        for row in rows:
            source = row["Source of referral"] or "No source"
            geographic = row["Geographic area"] or "No area recorded"
            disease = row["Referral disease"] or "No referral disease recorded"
            if disease.islower():
                disease = disease.title()
            # Trim this down because its too long for the row
            if disease == "Pulmonary fibrosis(e.g.: Asbestos related disease)":
                disease = "Pulmonary fibrosis"
            source_of_referral[source] += 1
            geographic_area[geographic] += 1
            referral_disease[disease] += 1

        other_area = 0
        area_to_remove = []
        for k, v in geographic_area.items():
            if v < 10 and not k == "No area recorded":
                area_to_remove.append(k)
                other_area += v
        for t in area_to_remove:
            geographic_area.pop(t)
        geographic_area["Other (< 10 patients)"] = other_area

        other_disease = 0
        disease_to_remove = []
        for k, v in referral_disease.items():
            if v < 5 and not k == "No referral disease recorded":
                disease_to_remove.append(k)
                other_disease += v
        for t in disease_to_remove:
            referral_disease.pop(t)
        referral_disease["Other (< 5 patients)"] = other_disease

        return {
            "Source of referral": dict(
                sorted(source_of_referral.items(), key=lambda x: -x[1])
            ),
            "Geographic area": dict(
                sorted(geographic_area.items(), key=lambda x: -x[1])
            ),
            "Referral disease": dict(
                sorted(referral_disease.items(), key=lambda x: -x[1])
            )
        }

    def get_clinician(self, rows):
        seen_by = defaultdict(int)
        peak_flows_requested = defaultdict(int)
        diagnosis_result = defaultdict(int)

        for row in rows:
            seen_by_name = row["Seen by"]
            if seen_by_name:
                seen_by_name = seen_by_name.upper()
            else:
                seen_by_name = "Unknown"

            seen_by[seen_by_name] += 1
            if not row["Peak flow"] == "Not requested":
                peak_flows_requested[seen_by_name] += 1
            if row["Diagnosis outcome"] == "Known":
                diagnosis_result[seen_by_name] += 1

        return {
            "Seen by": dict(sorted(seen_by.items(), key=lambda x: x[0])),
            "Peak flows requested": dict(sorted(
                peak_flows_requested.items(), key=lambda x: x[0]
            )),
            "Diagnosis known": dict(sorted(
                diagnosis_result.items(), key=lambda x: x[0]
            )),
        }

    def get_occupational_categories(self, rows):
        """
        Returns a dict of category to count, ordered by
        largest to smallest (then with no category at the end)
        """
        by_category = defaultdict(int)
        no_category = 0
        for row in rows:
            emp_category = row["Employment category"]
            if emp_category:
                by_category[emp_category] += 1
            else:
                no_category += 1

        category_order = [i for i in sorted(by_category.items(), key=lambda x: -x[1])]
        result = dict(category_order)
        result["No category"] = no_category
        return result

    def get_investigations_summary(self, rows):
        skin_prick_tests = defaultdict(int)
        peak_flow_response = defaultdict(int)
        bloods = defaultdict(int)
        by_spirometry_origin = defaultdict(int)

        for row in rows:
            spt = "No skin prick tests"
            if row["General SPT"] and row["Specific SPT"]:
                spt = "General atopy & specific SPT"
            elif row["General SPT"]:
                spt = "General atopy screen"
            elif row["Specific SPT"]:
                spt = "Specific occupational skin testing"
            skin_prick_tests[spt] += 1

            peak_flow_response[row["Peak flow"]] += 1
            by_spirometry_origin[row["Spirometry"]] += 1

            if row["Bloods"]:
                bloods["Bloods tested"] += 1
            else:
                bloods["No bloods"] += 1

        return {
            "Peak flow responses": sorted(
                list(peak_flow_response.items()), key=lambda x: -x[1]
            ),
            "Patients who had skin prick tests": sorted(
                list(skin_prick_tests.items()), key=lambda x: -x[1]
            ),
            "Patients who had bloods": sorted(
                list(bloods.items()), key=lambda x: -x[1]
            ),
            "Spirometry origin": sorted(
                list(by_spirometry_origin.items()), key=lambda x: -x[1]
            ),
        }

    def get_specific_skin_prick_tests(self, rows):
        by_spt = defaultdict(int)
        less_than_2 = 0
        for row in rows:
            if row["Specific SPT"]:
                for specific in row["Specific SPT"]:
                    by_spt[specific.title()] += 1

        for spt, amount in list(by_spt.items()):
            if amount < 2:
                less_than_2 += 1
                by_spt.pop(spt)
        result = dict(sorted(by_spt.items(), key=lambda x: -x[1]))
        if less_than_2:
            result["Other (<2)"] = less_than_2
        return result

    def get_oem_investigations(self, rows):
        result = defaultdict(int)
        stored = 0
        for row in rows:
            for test_type in row["Bloods"]:
                result[test_type] += 1

            if row["Bloods stored"]:
                stored += 1

        result = dict(sorted(result.items(), key=lambda x: x[0]))
        result["Bloods stored"] = stored
        return {
            "x": list(result.keys()),
            "vals": [
                [""] + list(result.values()),
            ]
        }

    def get_diagnosis_summary(self, rows):
        occupational_ratio = defaultdict(int)
        diagnosis_category = defaultdict(int)
        diagnosis_outcome = defaultdict(int)
        for row in rows:
            occupational, total = row["Occupational diagnosis"].split("/")
            occupational = int(occupational)
            total = int(total)
            occupational_ratio["Occupational"] += occupational
            occupational_ratio["Non occupational"] += total - occupational
            diagnosis_outcome[row["Diagnosis outcome"]] += 1
            for category in row["Diagnosis category"]:
                diagnosis_category[category] += 1

        return {
            "Diagnosis outcome": dict(sorted(
                diagnosis_outcome.items(), key=lambda x: -x[1]
            )),
            "Diagnosis category": dict(sorted(
                diagnosis_category.items(), key=lambda x: -x[1]
            )),
            "Occupational diagnosis": dict(sorted(
                occupational_ratio.items(), key=lambda x: -x[1]
            )),
        }

    def get_diagnosis_breakdown(self, rows):
        by_diagnosis = defaultdict(int)
        other_less_than_3 = 0
        for row in rows:
            for diagnosis in row["Diagnosis"]:
                by_diagnosis[diagnosis] += 1

        for diagnosis, amount in list(by_diagnosis.items()):
            if amount < 3:
                other_less_than_3 += amount
                by_diagnosis.pop(diagnosis)

        result = dict(sorted(by_diagnosis.items(), key=lambda x: -x[1]))
        if other_less_than_3:
            result["Other (<3)"] = other_less_than_3
        return result

    def get_aggregates(self):
        rows = self.get_rows()
        result = {}
        if not rows:
            return {}
        result["head_lines"] = self.get_head_lines(rows)
        result["patient_flow"] = self.get_flow(rows)
        result["referral"] = self.get_referral(rows)
        result["demographics"] = self.get_demographics(rows)
        result["occupational_categories"] = self.get_occupational_categories(rows)
        result["by_clinician"] = self.get_clinician(rows)
        result["investigations_summary"] = self.get_investigations_summary(rows)
        result["specific_skin_prick_tests"] = self.get_specific_skin_prick_tests(rows)
        result["oem_investigations"] = self.get_oem_investigations(rows)
        result["diagnosis_summary"] = self.get_diagnosis_summary(rows)
        result["diagnosis_breakdown"] = self.get_diagnosis_breakdown(rows)
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
