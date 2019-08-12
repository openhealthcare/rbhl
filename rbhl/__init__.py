"""
rbhl - Our Opal Application
"""
from opal.core import application, menus
from django.urls import reverse

from rbhl.episode_categories import OccupationalLungDiseaseEpisode


class Application(application.OpalApplication):
    javascripts   = [
        'js/rbhl/routes.js',
        'js/rbhl/clinicdatecomparator.js',
        'js/opal/controllers/discharge.js',
        'js/rbhl/directives.js',
        'js/rbhl/controllers/peak_flow_ctrl.js',
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
        from rbhl.pathways import NewReferral

        items = [
            NewReferral.as_menuitem(index=1),
            menus.MenuItem(
                activepattern=reverse('active-list'),
                href=reverse('active-list'),
                display=('Active patients'),
                icon="fa-table"
            ),
            menus.MenuItem(
                activepattern=reverse('mine-list'),
                href=reverse('mine-list'),
                display=('Seen by me'),
                icon="fa-table"
            )
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
