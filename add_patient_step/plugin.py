"""
Plugin definition for the add_patient_step Opal plugin
"""
from opal.core import plugins

from add_patient_step.urls import urlpatterns
from add_patient_step import api


class add_patient_stepPlugin(plugins.OpalPlugin):
    """
    Main entrypoint to expose this plugin to our Opal application.
    """
    urls = urlpatterns
    javascripts = {
        'opal.services': [
            'js/add_patient_step/services/demographics_search.js',
        ],
        'opal.controllers': [
            'js/add_patient_step/controllers/look_up_patient.js'
        ]
    }

    def list_schemas(self):
        """
        Return any patient list schemas that our plugin may define.
        """
        return {}

    def roles(self, user):
        """
        Given a (Django) USER object, return any extra roles defined
        by our plugin.
        """
        return {}

    apis = [
        ("demographics_search", api.DemographicsSearch,),
    ]

    opal_angular_exclude_tracking_qs = [
        "/new_referral",
    ]
