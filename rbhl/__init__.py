"""
rbhl - Our Opal Application
"""
from opal.core import application, menus

from rbhl.episode_categories import OccupationalLungDiseaseEpisode


class Application(application.OpalApplication):
    javascripts   = [
        'js/rbhl/routes.js',
        'js/rbhl/clinicdatecomparator.js',
        'js/rbhl/controllers/peak_flow_ctrl.js',
        'js/opal/controllers/discharge.js',
        # Uncomment this if you want to implement custom dynamic flows.
        # 'js/rbhl/flow.js',
    ]
    styles = [
        'css/rbhl.css'
    ]

    default_episode_category = OccupationalLungDiseaseEpisode.display_name

    @classmethod
    def get_menu_items(klass, user=None):
        # we import here as settings must be set before this is imported
        from rbhl.patient_lists import ActivePatients
        from rbhl.pathways import NewReferral

        items = [
            NewReferral.as_menuitem(index=1),
            ActivePatients.as_menuitem(index=2),
        ]
        if user:
            if user.is_authenticated:
                if user.is_staff:
                    items.append(
                        menus.MenuItem(
                            href="/admin/", icon="fa-cogs", display="Admin",
                            index=999
                        )
                    )
        return items
