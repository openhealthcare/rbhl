import datetime
import json
import tempfile
import zipfile
import os
import csv
import io
from pathlib import Path
from collections import defaultdict
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import ListView, DetailView, TemplateView
from dateutil.relativedelta import relativedelta
from plugins.lab.models import BloodResult, Bloods


class ZipCsvWriter:
    """
    Write a list of dicts to a zip file

    example code

    with ZipCsvWriter("extract01092020") as z:
        z.write_csv("allergens.cvs", [{"allergen": "flour"}])

    return z.name
    """
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def __enter__(self):
        temp_dir = tempfile.mkdtemp()
        zip_file = os.path.join(temp_dir, f'{self.folder_name}')
        self.zipfile = zipfile.ZipFile(zip_file, mode='w')
        return self

    def write_csv(self, file_name, list_of_dicts):
        buffer = io.StringIO()
        wr = None
        if list_of_dicts:
            headers = list_of_dicts[0].keys()
            wr = csv.DictWriter(
                buffer, field_names=headers
            )
            wr.writerows(list_of_dicts)
        self.zipfile.writestr(file_name, buffer.get_value())

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


class LabReport(DetailView):
    model = Bloods
    template_name = "lab_report.html"


class LabOverview(TemplateView):
    template_name = "stats/lab_overview.html"

    @cached_property
    def date_ranges(self):
        ranges = []
        start_date = datetime.date.today()
        month_start = datetime.date(
            start_date.year, start_date.month, 1
        )
        if not start_date == month_start:
            date_range = [(start_date, month_start)]
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
        Number of distinct blood numbers received
        and number of blood results created
        """
        date_ranges = self.date_ranges
        number_of_samples_received = {}
        number_of_tests_assayed = {}
        for month_start, month_end in date_ranges:
            my = f"{month_start.month}/{month_start.year}"

            number_of_samples_received[my] = len(set(Bloods.objects.filter(
                blood_date__gte=month_start,
                blood_date__lt=month_end
            ).values_list("blood_number").distinct()))

            number_of_tests_assayed[my] = BloodResult.objects.filter(
                bloods__blood_date__gte=month_start,
                bloods__blood_date__lt=month_end
            ).count()

        return {
            "Number of samples received": number_of_samples_received,
            "Number of tests assayed": number_of_tests_assayed
        }

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
        result = {}
        for exposure in exposures:
            result[exposure] = {
                dt: by_exposure[exposure] for dt, by_exposure in by_month.items()
            }
        return result

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
                if employment.employer and employment.oh_provider:
                    employer_referrer = "{}/{}".format(
                        employment.employer, employment.oh_provider
                    )
                else:
                    employer_referrer = employment.employer or employment.oh_provider
                by_provider[employer_referrer] += 1
                oh_providers.add(employer_referrer)
            by_month[my] = by_provider
        oh_providers = sorted(list(oh_providers))
        result = {}

        result = {}
        for oh_provider in oh_providers:
            result[oh_provider] = {
                dt: by_provider[oh_provider] for dt, by_provider in by_month.items()
            }
        return result

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        overview = self.get_overview()
        ctx["table_data"] = [
            overview,
            self.get_requests_by_exposure(),
            self.get_requests_by_oh_provider()
        ]
        graph_data = [["x"] + [i[0].strftime("%Y-%m-%d") for i in self.date_ranges]]
        for k, v in overview.items():
            graph_data.append(
                [k] + list(v.values())
            )
        ctx["graph_data"] = json.dumps(graph_data)
        return ctx
