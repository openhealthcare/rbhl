"""
Plugin definition for the RBH legacy databases
"""
from opal.core import plugins
from legacy.urls import urlpatterns


class LegacyPlugin(plugins.OpalPlugin):
    """
    Expose this plugin to our Opal application
    """
    urls = urlpatterns
    javascripts = {
        'opal.controllers': [
            'js/legacy/controllers/blood_book.js'
        ]
    }
