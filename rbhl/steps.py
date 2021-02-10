from opal.core.pathway import Step
from django.urls import reverse_lazy


class DemographicsSearchStep(Step):
    """
    A step that requests the user enters name or hospital number.

    If we find patients is offers a list for them to click through
    to.

    Otherwise it offers a demographics form.
    """
    template = "pathway/demographics_search/demographics_search_form.html"
    step_controller = "DemographicsSearchCtrl"
    display_name = "Find patient"
    icon = "fa fa-user"

    # an end point that takes a get parameter of hospital_number
    search_end_point = reverse_lazy("simple_search")

    def to_dict(self, *args, **kwargs):
        dicted = super().to_dict(*args, **kwargs)
        dicted["search_end_point"] = str(self.search_end_point)
        return dicted
