import datetime
import json
import tempfile
import zipfile
import os
import csv
import io
import statistics
import holidays
from pathlib import Path
from collections import defaultdict
from django.http import HttpResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.views.generic import ListView, DetailView, TemplateView
from dateutil.relativedelta import relativedelta
from plugins.lab.models import BloodResult, Bloods


class ZipCsvWriter:
    """
    Write a list of dicts to a zip file

    example code

    with ZipCsvWriter("extract01092020.zip"") as z:
        z.write_csv("allergens.cvs", [{"allergen": "flour"}])

    return z.name
    """
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def __enter__(self):
        temp_dir = tempfile.mkdtemp()
        self.zip_file_name = os.path.join(temp_dir, f'{self.folder_name}')
        self.zipfile = zipfile.ZipFile(self.zip_file_name, mode='w')
        return self

    def write_csv(self, file_name, list_of_dicts):
        buffer = io.StringIO()
        wr = None
        if list_of_dicts:
            headers = list_of_dicts[0].keys()
            wr = csv.DictWriter(
                buffer, fieldnames=headers
            )
            wr.writeheader()
            wr.writerows(list_of_dicts)
        self.zipfile.writestr(file_name, buffer.getvalue())

    @property
    def name(self):
        return self.zip_file_name

    def __exit__(self, *args):
        self.zipfile.close()


def zip_file_to_response(file_with_path):
    with open(file_with_path, 'rb') as download:
        content = download.read()

    file_name = Path(file_with_path).name
    resp = HttpResponse(content)
    disp = f'attachment; filename="{file_name}"'
    resp['Content-Disposition'] = disp
    return resp


class UnresultedList(ListView):
    queryset = Bloods.objects.filter(bloodresult=None).exclude(
        room=""
    ).prefetch_related(
        "patient__demographics_set"
    )
    template_name = 'patient_lists/unresulted_list.html'

    def get_ordering(self):
        order_param = self.request.GET.get("order")
        if not order_param:
            return "-blood_date"
        if order_param == "name":
            return "patient__demographics__first_name"

        if order_param == "-name":
            return "-patient__demographics__first_name"

        return order_param


class YourRecentlyResultedList(ListView):
    model = Bloods
    template_name = 'patient_lists/recently_resulted.html'
    AMOUNT = 50

    def initials(self):
        first_name = self.request.user.first_name or " "
        surname = self.request.user.last_name or " "
        return "{}{}".format(first_name[0], surname[0]).strip().upper()

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).exclude(
            assay_date=None
        )
        initials = self.initials()
        if initials:
            qs = qs.filter(
                patient__episode__cliniclog__seen_by__icontains=self.initials()
            )
            return qs.order_by("-assay_date")[:self.AMOUNT]
        return qs.none()


class RecentlyRecievedSamples(ListView):
    model = Bloods
    template_name = 'patient_lists/recently_received_samples.html'

    def get_queryset(self, *args, **kwargs):
        two_months_ago = timezone.now() - datetime.timedelta(60)
        return Bloods.objects.filter(
            blood_date__gte=two_months_ago.date()
        ).prefetch_related(
            "patient__demographics_set"
        ).prefetch_related(
            "patient__episode_set"
        )

    def get_rows(self, queryset):
        rows = []
        order_param = self.request.GET.get("order")
        if not order_param:
            queryset = queryset.order_by("-blood_date")

        for instance in queryset:
            episode = list(instance.patient.episode_set.all())[-1]
            referral = episode.referral_set.last()
            employment = episode.employment_set.last()
            oh_provider = ""
            employer = ""
            ref_number = ""
            if employment:
                if employment.oh_provider:
                    oh_provider = employment.oh_provider
                if employment.employer:
                    employer = employment.employer
            if referral:
                ref_number = referral.reference_number
            demographics = instance.patient.demographics_set.all()[0]
            rows.append({
                "Name": demographics.name,
                "Hospital number": demographics.hospital_number,
                "OH Provider": oh_provider,
                "Employer": employer,
                "Their ref number": ref_number or "",
                "Blood number": instance.blood_number,
                "Exposure": instance.exposure,
                "Sample received": instance.blood_date or "",
                "Report submitted": instance.report_st or "",
                "patient_id": instance.patient_id
            })

        if order_param:
            reverse = False
            if order_param.startswith("-"):
                reverse = True
                order_param = order_param.lstrip("-")
            if order_param in ["Sample received", "Report submitted"]:
                min_date = datetime.datetime.min.date()
                # you can't sort by a mix of datetime and None, make None become
                # datetime.datetime.min for the purposese of sorting
                return sorted(
                    rows, key=lambda x: x[order_param] or min_date, reverse=reverse
                )
            return sorted(rows, key=lambda x: x[order_param], reverse=reverse)
        return rows

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["rows"] = self.get_rows(ctx["object_list"])
        return ctx


class LabReport(DetailView):
    model = Bloods
    template_name = "lab_report.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        results = self.object.bloodresult_set.all()
        ctx["has_kul"] = any(i for i in results if i.kul)
        ctx["has_rast"] = any(i for i in results if i.rast)
        return ctx


class AbstractLabStatsPage(TemplateView):
    def menu_dates(self):
        result = []
        today = datetime.date.today()
        if today.day == 1:
            date_range = range(1, 7)
        else:
            date_range = range(6)

        for i in reversed(date_range):
            result.append(today - relativedelta(months=i))
        return result


class LabOverview(AbstractLabStatsPage):
    template_name = "stats/lab_overview.html"

    @cached_property
    def date_ranges(self):
        ranges = []
        start_date = datetime.date.today()
        month_start = datetime.date(
            start_date.year, start_date.month, 1
        )
        if not start_date == month_start:
            ranges = [(month_start, month_start + relativedelta(months=1))]
            num_months = 11
        else:
            num_months = 12

        for i in range(0, num_months):
            date_range = (
                month_start - relativedelta(months=i+1),
                month_start - relativedelta(months=i)
            )
            ranges.append(date_range)
        return sorted(ranges)

    def get_overview(self):
        """
        Number of distinct blood numbers received,
        Number of blood numbers exposures tested,
        and number of blood results created
        """
        date_ranges = self.date_ranges
        number_of_samples_received = {"name": "Samples received"}
        number_of_exposures = {"name": "Exposure tests on samples"}
        number_of_tests_assayed = {"name": "Tests assayed"}
        for month_start, month_end in date_ranges:
            my = month_start.strftime('%b/%y')

            bloods = Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            )
            number_of_samples_received[my] = len(set([i.blood_number for i in bloods]))
            number_of_exposures[my] = len(
                set([(i.blood_number, i.exposure,) for i in bloods])
            )
            number_of_tests_assayed[my] = BloodResult.objects.filter(
                bloods__blood_date__gte=month_start,
                bloods__blood_date__lt=month_end
            ).count()

        rows = [
            number_of_samples_received, number_of_exposures, number_of_tests_assayed
        ]
        return rows

    def get_requests_by_exposure(self):
        """
        Number of bloods by exposure
        """
        date_ranges = self.date_ranges
        by_month = {}
        exposures = set()

        for month_start, month_end in date_ranges:
            my = month_start.strftime('%b/%y')
            by_exposure = defaultdict(int)
            bloods = Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            )
            for blood in bloods:
                exposure = blood.exposure
                if not exposure:
                    exposure = "No exposure"
                by_exposure[exposure] += 1
                exposures.add(exposure)
            by_month[my] = by_exposure

        exposures = sorted(list(exposures))
        rows = []
        for exposure in exposures:
            row = {"name": exposure}
            for dt, by_exposure in by_month.items():
                row[dt] = by_exposure[exposure]
            rows.append(row)
        return rows

    def get_requests_by_oh_provider(self):
        """
        Number of distinct blood numbers received by oh provider
        """
        by_month = {}
        oh_providers = set()
        for month_start, month_end in self.date_ranges:
            blood_nums_seen = set()
            my = month_start.strftime('%b/%y')
            by_provider = defaultdict(int)
            bloods = Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            )
            for blood in bloods:
                if blood.blood_number in blood_nums_seen:
                    continue
                blood_nums_seen.add(blood.blood_number)
                employment = blood.employment
                employer_referrer = None
                if employment and employment.employer and employment.oh_provider:
                    employer_referrer = "{}/{}".format(
                        employment.employer, employment.oh_provider
                    )
                elif employment:
                    employer_referrer = employment.employer or employment.oh_provider
                if not employer_referrer:
                    employer_referrer = "No employer"

                if blood.referral and blood.referral.occld:
                    employer_referrer = f"{employer_referrer} (OCCLD)"
                by_provider[employer_referrer] += 1
                oh_providers.add(employer_referrer)
            by_month[my] = by_provider
        oh_providers = sorted(list(oh_providers))
        rows = []
        for oh_provider in oh_providers:
            row = {"name": oh_provider}
            for dt, by_provider in by_month.items():
                row[dt] = by_provider[oh_provider]
            rows.append(row)
        return rows

    def get_table_data(self):
        return {
            "Overview": self.get_overview(),
            "By exposure": self.get_requests_by_exposure(),
            "By OH provider": self.get_requests_by_oh_provider()
        }

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["table_data"] = self.get_table_data()
        graph_data = [["x"] + [i[0].strftime("%Y-%m-%d") for i in self.date_ranges]]

        # add the overview data for the graphs
        graph_data.extend([list(i.values()) for i in ctx["table_data"]["Overview"]])
        ctx["graph_data"] = json.dumps(graph_data)
        menu_dates = self.date_ranges[-3:]
        menu_dates.reverse()
        ctx["menu_dates"] = [month[0] for month in menu_dates]
        return ctx

    def post(self, *args, **kwargs):
        zip_file_name = "lab_summary.zip"
        table_data = self.get_table_data()
        with ZipCsvWriter(zip_file_name) as zf:
            rows = []
            for section_name, row_set in table_data.items():
                if not section_name == "Overview":
                    rows.append({"name": section_name})
                rows.extend(row_set)
                rows.append({})
            zf.write_csv(
                "lab_summary.csv", rows
            )
        return zip_file_to_response(zf.name)


class LabMonthActivity(AbstractLabStatsPage):
    template_name = "stats/lab_month_activity.html"

    @cached_property
    def holidays(self):
        return holidays.UnitedKingdom()

    def get_row(self, blood):
        patient_id = blood.patient_id
        episode_id = blood.patient.episode_set.last().id
        employment = blood.employment
        employer = "No employer"
        oh_provider = "No OH provider"
        if employment and employment.employer:
            employer = employment.employer

        if employment and employment.oh_provider:
            oh_provider = employment.oh_provider

        referral = blood.referral
        referral_source = "No referral source"
        reference_number = "No reference number"
        if referral:
            if referral.referral_source:
                referral_source = referral.referral_source
            if referral.occld:
                referral_source = f"{referral_source} (OCCLD)"
            reference_number = referral.reference_number
        demographics = blood.patient.demographics_set.all()[0]
        row = {
            "Link": f"/pathway/#/bloods/{patient_id}/{episode_id}?id={blood.id}",
            "Sample received": blood.blood_date,
            "Referral source": referral_source,
            "Reference number": reference_number,
            "Hospital number": demographics.hospital_number,
            "Surname": demographics.surname,
            "OH Provider": oh_provider,
            "Blood num": blood.blood_number,
            "Employer": employer,
            "Exposure": blood.exposure or "No exposure",
            "Allergens": sorted(
                list(i.allergen for i in blood.bloodresult_set.all() if i.allergen)
            ),
            "Report submitted": blood.report_st,
            "Num tests": blood.bloodresult_set.count(),
        }
        if blood.report_st and blood.blood_date:
            # dates are usually inclusive, e.g. 2nd - 5th if 4 days not 3
            row["Days"] = self.get_day_count(blood.blood_date, blood.report_st)
        else:
            row["Days"] = ""
        return row

    def get_queryset(self, month, year):
        return Bloods.objects.filter(blood_date__month=month).filter(
            blood_date__year=year
        ).select_related(
            "employment", "referral"
        ).prefetch_related(
            'patient__demographics_set'
        ).order_by("blood_date")

    def get_rows(self, month, year):
        bloods = self.get_queryset(month, year)
        result = []
        for blood in bloods:
            result.append(self.get_row(blood))
        return result

    def get_day_count(self, start_dt, report_date):
        """
        Returns the count of week days inclusive
        between the blood date and the report date

        It also excludes bank holidays
        """
        count = 0
        if start_dt > report_date:
            return count
        while start_dt <= report_date:
            if start_dt.weekday() < 5:
                if start_dt not in self.holidays:
                    count += 1
            start_dt = start_dt + datetime.timedelta(1)
        return count

    def get_multi_mode(self, some_list):
        """
        In python 3.8 we can use statistics.multimode

        statistics.mode fails if there are multipe of the
        same values, this returns this as a list
        """
        if not some_list:
            return
        if len(some_list) == 1:
            return [some_list[0]]
        result = defaultdict(int)
        for some_val in some_list:
            result[some_val] += 1
        largest = max(*result.values())
        return [i for i, v in result.items() if v == largest]

    def get_summary(self, rows):
        days = [i["Days"] for i in rows if not i["Days"] == ""]
        if days:
            num_tests = [i["Num tests"] for i in rows if not i["Days"] == ""]
            mean_days = "{:.2f}".format(statistics.mean(days))
            mode_days = ", ".join([str(i) for i in self.get_multi_mode(days)])
            num_days_gt_5 = len([
                i["Num tests"] for i in rows if not i["Days"] == "" and i["Days"] > 5
            ])
            return [
                {"type": "Num tests", "value": sum(num_tests)},
                {
                    "type": "Num samples",
                    "value": len({i["Blood num"] for i in rows})
                },
                {
                    "type": "Mean response (days)", "value": mean_days,
                },
                {"type": "Median response (days)", "value": statistics.median(days)},
                {"type": "Mode response (days)", "value": mode_days},
                {"type": "Num days > 5", "value": num_days_gt_5}
            ]
        return []

    def get_employers_pie_chart(self, rows):
        by_employer = defaultdict(int)
        for row in rows:
            by_employer[row["Employer"]] += 1
        return sorted([[i, v] for i, v in by_employer.items()], key=lambda x: x[0])

    def get_exposure_pie_chart(self, rows):
        by_exposure = defaultdict(int)
        for row in rows:
            by_exposure[row["Exposure"]] += 1
        return sorted([[i, v] for i, v in by_exposure.items()], key=lambda x: x[0])

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        year = int(kwargs["year"])
        month = int(kwargs["month"])
        ctx["date"] = datetime.date(year, month, 1)
        ctx["rows"] = self.get_rows(month, year)
        ctx["summary"] = self.get_summary(ctx["rows"])
        ctx["employer_pie_chart"] = json.dumps(
            self.get_employers_pie_chart(ctx["rows"])
        )
        ctx["exposure_pie_chart"] = json.dumps(self.get_exposure_pie_chart(ctx["rows"]))
        return ctx

    def get_results_rows(self, month, year):
        """
        Returns the employer rows at the granularity
        of bloods results
        """
        bloods = self.get_queryset(month, year)
        bloods = bloods.prefetch_related('bloodresult_set')
        max_row_count = 0
        if bloods:
            max_row_count = max(
                [len(i.bloodresult_set.all()) for i in bloods]
            )
        rows = []
        for blood in bloods:
            referrer_name = ""
            if blood.referral:
                referrer_name = blood.referral.referrer_name
            employer = ""
            if blood.employment:
                employer = blood.employment.employer
            demographics = blood.patient.demographics_set.all()[0]
            row = {
                "Blood num": blood.blood_number,
                "Referrer name": referrer_name,
                "Sample received": blood.blood_date,
                "Surname": demographics.surname,
                "DOB": demographics.date_of_birth,
                "Employer": employer
            }
            for idx, result in enumerate(blood.bloodresult_set.all(), 1):
                row[f"Allergen {idx}"] = result.allergen
                row[f"KU/L {idx}"] = result.kul
                row[f"IgE Class {idx}"] = result.klass
                row[f"RAST {idx}"] = result.rast
                row[f"RAST score {idx}"] = result.rast_score
                row[f"Precipitin {idx}"] = result.precipitin
                row[f"IgG {idx}"] = result.igg
                row[f"IgG Class {idx}"] = result.iggclass
            results_len = len(blood.bloodresult_set.all())
            for idx in range(results_len + 1, max_row_count):
                row[f"Allergen {idx}"] = ""
                row[f"KU/L {idx}"] = ""
                row[f"IgE Class {idx}"] = ""
                row[f"RAST {idx}"] = ""
                row[f"RAST score {idx}"] = ""
                row[f"Precipitin {idx}"] = ""
                row[f"IgG {idx}"] = ""
                row[f"IgG Class {idx}"] = ""
            rows.append(row)
        return rows

    def post(self, *args, **kwargs):
        zip_file_name = "lab_summary.zip"
        year = int(kwargs["year"])
        month = int(kwargs["month"])
        dt = datetime.date(year, month, 1)
        month_name = dt.strftime("%B").lower()
        zip_file_name = f"{month_name}_review.zip"
        rows = self.get_rows(month, year)
        result_rows = self.get_results_rows(month, year)
        for row in rows:
            scheme = self.request.scheme
            host = self.request.get_host()
            row["Link"] = f"{scheme}://{host}{row['Link']}"
            row["Allergens"] = ", ".join(row["Allergens"])
        summary = self.get_summary(rows)
        employers = list({i["Employer"] for i in rows if i})

        with ZipCsvWriter(zip_file_name) as zf:
            zf.write_csv("rows.csv", rows)
            zf.write_csv("summary.csv", summary)
            for row in rows:
                row.pop("Link")
            for employer in employers:
                employer_rows = [row for row in rows if row["Employer"] == employer]
                employer_name = employer.lower().replace(" ", "_")
                zf.write_csv(
                    f"oem_{employer_name}_{month_name}_{year}.csv", employer_rows
                )
                employer_results_rows = [
                    row for row in result_rows if row["Employer"] == employer
                ]
                zf.write_csv(
                    f"oem_{employer_name}_invoice_{month_name}_{year}.csv",
                    employer_results_rows
                )

        return zip_file_to_response(zf.name)
