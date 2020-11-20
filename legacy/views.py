from django.views.generic import ListView
from legacy.models import BloodBook


class UnresultedList(ListView):
    queryset = BloodBook.objects.filter(bloodbookresult=None).exclude(
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
