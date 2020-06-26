from opal.core import detail


class Investigations(detail.PatientDetailView):
    order = 5
    template = "datail/investigations.html"
