import csv
import datetime
import io
from django.http import HttpResponse
from django.utils import timezone
import json
import tempfile
import zipfile
import os
import statistics
from pathlib import Path
from collections import defaultdict
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

    def post(self, *args, **kwargs):
        qs = self.get_queryset()
        rows = self.get_rows(qs)
        for row in rows:
            patient_id = row.pop("patient_id")
            row["indigo link"] = "{}://{}/#/patient/{}".format(
                self.request.scheme,
                self.request.get_host(),
                patient_id
            )
        buffer = io.StringIO()
        if rows:
            field_names = list(rows[0].keys())
            field_names.remove("indigo link")
            field_names.insert(0, "indigo link")
            wr = csv.DictWriter(buffer, fieldnames=field_names)
            wr.writeheader()
            wr.writerows(rows)
            buffer.seek(0)
        resp = HttpResponse(buffer, content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename=recent_samples.csv'
        return resp

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
            employer = episode.employment_set.last()
            oh_provider = ""
            ref_number = ""
            if employer:
                oh_provider = employer.oh_provider
            if referral:
                ref_number = referral.reference_number
            demographics = instance.patient.demographics_set.all()[0]
            rows.append({
                "Name": demographics.name,
                "Hospital number": demographics.hospital_number,
                "OH Provider": oh_provider,
                "Employer": employer.employer,
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


class AbstractLabStatsPage(TemplateView):
    def menu_dates(self):
        result = []
        today = datetime.date.today()
        for i in reversed(range(3)):
            result.append(today - relativedelta(months=i+1))
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
            num_months = 5
        else:
            num_months = 6

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
        number_of_samples_received = {"name": "Number of samples received"}
        number_of_exposures = {"name": "Number of exposures tests on samples"}
        number_of_tests_assayed = {"name": "Number of tests assayed"}
        for month_start, month_end in date_ranges:
            my = f"{month_start.month}/{month_start.year}"

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
            my = f"{month_start.month}/{month_start.year}"
            by_exposure = defaultdict(int)
            bloods = Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            )
            for blood in bloods:
                by_exposure[blood.exposure] += 1
                exposures.add(blood.exposure)
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
            my = f"{month_start.month}/{month_start.year}"
            by_provider = defaultdict(int)
            bloods = Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            )
            for blood in bloods:
                if blood.blood_number in blood_nums_seen:
                    continue
                blood_nums_seen.add(blood.blood_number)
                employment = blood.get_employment()
                if employment and employment.employer and employment.oh_provider:
                    employer_referrer = "{}/{}".format(
                        employment.employer, employment.oh_provider
                    )
                elif employment:
                    employer_referrer = employment.employer or employment.oh_provider
                else:
                    employer_referrer = "None entered"
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

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        overview = self.get_overview()
        ctx["table_data"] = [
            overview,
            self.get_requests_by_exposure(),
            self.get_requests_by_oh_provider()
        ]
        graph_data = [["x"] + [i[0].strftime("%Y-%m-%d") for i in self.date_ranges]]
        graph_data.extend([list(i.values()) for i in overview])
        ctx["graph_data"] = json.dumps(graph_data)
        menu_dates = self.date_ranges[-3:]
        menu_dates.reverse()
        ctx["menu_dates"] = [month[0] for month in menu_dates]
        return ctx

    def post(self, *args, **kwargs):
        zip_file_name = "lab_summary.zip"
        with ZipCsvWriter(zip_file_name) as zf:
            rows = []
            rows.extend(self.get_overview())
            rows.append({})
            rows.extend(self.get_requests_by_exposure())
            rows.append({})
            rows.extend(self.get_requests_by_oh_provider())
            zf.write_csv(
                "lab_summary.csv", rows
            )
        return zip_file_to_response(zf.name)


class LabMonthReview(AbstractLabStatsPage):
    template_name = "stats/lab_month_review.html"

    def get_rows(self, month, year):
        bloods = Bloods.objects.filter(blood_date__month=month).filter(
            blood_date__year=year
        ).order_by("blood_date")
        result = []
        for blood in bloods:
            patient_id = blood.patient_id
            episode_id = blood.patient.episode_set.last().id
            employment = blood.get_employment()
            row = {
                "Link": f"/pathway/#/bloods/{patient_id}/{episode_id}?id={blood.id}",
                "Sample received": blood.blood_date,
                "OH Provider": employment.oh_provider,
                "Blood num": blood.blood_number,
                "Employer": employment.employer,
                "Exposure": blood.exposure,
                "Allergens": ", ".join(
                    sorted(list({i.allergen for i in blood.bloodresult_set.all()}))
                ),
                "Report submitted": blood.report_st,
                "Num tests": blood.bloodresult_set.count(),
            }
            if blood.report_st and blood.blood_date:
                row["Days"] = (blood.report_st - blood.blood_date).days
            else:
                row["Days"] = ""
            result.append(row)
        return result

    def get_multi_mode(self, some_list):
        """
        In python 3.8 we can use statistics.multimode

        statistics.mode fails if there are multipe of the
        same values, this returns this as a list
        """
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
            return [
                {"type": "Num tests", "value": sum(num_tests)},
                {
                    "type": "Mean response (days)", "value": mean_days,
                },
                {"type": "Median response (days)", "value": statistics.median(days)},
                {"type": "Mode response (days)", "value": mode_days},
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

    def post(self, *args, **kwargs):
        zip_file_name = "lab_summary.zip"
        year = int(kwargs["year"])
        month = int(kwargs["month"])
        dt = datetime.date(year, month, 1)
        month_name = dt.strftime("%B").lower()
        zip_file_name = f"{month_name}_review.zip"
        rows = self.get_rows(month, year)
        for row in rows:
            row["Link"] = f"https://indigo-rbht.openhealthcare.org.uk{row['Link']}"
        summary = self.get_summary(rows)
        employers = list({i["Employer"] for i in rows})
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

        return zip_file_to_response(zf.name)
