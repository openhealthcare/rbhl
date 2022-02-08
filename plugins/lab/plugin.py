"""
Plugin definition for the lab Opal plugin
"""
from opal.core import plugins

from plugins.lab.urls import urlpatterns


class LabPlugin(plugins.OpalPlugin):
    """
    Main entrypoint to expose this plugin to our Opal application.
    """
    urls = urlpatterns
    javascripts = {
        'opal.controllers': [
            'js/lab/controllers/investigations.js',
            'js/lab/controllers/skin_prick_test_ctrl.js',
            'js/lab/controllers/bloods.js'
        ],
        'opal.services': [
            'js/lab/services/skin_prick_test_helper.js'
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
