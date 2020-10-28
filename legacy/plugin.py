"""
Plugin definition for the RBH legacy databases
"""
from opal.core import plugins


class LegacyPlugin(plugins.OpalPlugin):
    """
    Expose this plugin to our Opal application
    """
    javascripts = {
        'opal.controllers': [
            'js/legacy/controllers/blood_book.js'
        ]
    }
