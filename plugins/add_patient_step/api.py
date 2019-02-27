from opal.core.api import LoginRequiredViewset
from opal.core import subrecords
from django.conf import settings
from django.utils.module_loading import import_string
from django.http import HttpResponseBadRequest
from opal.core.views import json_response


class DemographicsSearch(LoginRequiredViewset):
    base_name = 'demographics-search'
    PATIENT_FOUND_IN_APPLICATION = "patient_found_in_application"
    PATIENT_FOUND_UPSTREAM = "patient_found_upstream"
    PATIENT_NOT_FOUND = "patient_not_found"

    def list(self, request, *args, **kwargs):
        Demographics = subrecords.get_subrecord_from_model_name("Demographics")
        hospital_number = request.query_params.get("hospital_number")
        if not hospital_number:
            return HttpResponseBadRequest("Please pass in a hospital number")
        demographics = Demographics.objects.filter(
            hospital_number=hospital_number
        ).last()

        # the patient is in elcid
        if demographics:
            return json_response(dict(
                patient=demographics.patient.to_dict(request.user),
                status=self.PATIENT_FOUND_IN_APPLICATION
            ))
        else:
            if hasattr(settings, "UPSTREAM_DEMOGRAPHICS_SERVICE"):
                upstream_demographics = import_string(
                    settings.UPSTREAM_DEMOGRAPHICS_SERVICE
                )
                demographics = upstream_demographics(hospital_number)

                if demographics:
                    return json_response(dict(
                        patient=dict(demographics=[demographics]),
                        status=self.PATIENT_FOUND_UPSTREAM
                    ))
        return json_response(dict(status=self.PATIENT_NOT_FOUND))

