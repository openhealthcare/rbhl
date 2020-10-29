"""
rbhl - Our Opal Application
"""
from opal.core import application, menus
from django.urls import reverse, reverse_lazy

from rbhl.episode_categories import OccupationalLungDiseaseEpisode
from rbhl import constants


class SeenByMeMenuItem(menus.MenuItem):
    def for_user(self, user):
        from opal.models import UserProfile
        return UserProfile.objects.filter(
            user=user,
            roles__name=constants.DOCTOR_ROLE
        ).exists()


seen_by_me_menu_item = SeenByMeMenuItem(
    activepattern=reverse_lazy('seen-by-me-list'),
    href=reverse_lazy('seen-by-me-list'),
    display='Seen by me',
    icon="fa-table"
)


class Application(application.OpalApplication):
    javascripts   = [
        'js/rbhl/routes.js',
        'js/rbhl/filters.js',
        'js/rbhl/clinicdatecomparator.js',
        'js/rbhl/directives.js',
        'js/rbhl/controllers/peak_flow_ctrl.js',
        'js/rbhl/controllers/diagnosis_display.js',
        'js/rbhl/services/peak_flow_graph_data_loader.js',
        'js/rbhl/controllers/peak_flow_step.js',
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
            )
        ]
        if user:
            if user.is_authenticated:
                if seen_by_me_menu_item.for_user(user):
                    items.append(seen_by_me_menu_item)
                if user.is_staff:
                    items.append(
                        menus.MenuItem(
                            href="/admin/", icon="fa-cogs", display="Admin",
                            index=999
                        )
                    )
                if user.profile.can_extract or user.is_superuser:
                    items.append(
                        menus.MenuItem(
                            href="/search/#/extract/",
                            icon="fa-search",
                            display="Query",
                            index=1999
                        )
                    )

        return items
