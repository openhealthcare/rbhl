"""
rbhl - Our Opal Application
"""
import datetime
from opal.core import application, menus
from django.urls import reverse, reverse_lazy

from rbhl.episode_categories import OccupationalLungDiseaseEpisode
from rbhl import constants


class DoctorMenuItem(menus.MenuItem):
    def for_user(self, user):
        from opal.models import UserProfile
        return UserProfile.objects.filter(
            user=user,
            roles__name=constants.DOCTOR_ROLE
        ).exists()


your_recently_resulted = DoctorMenuItem(
    activepattern=reverse_lazy('your-recently-resulted-list'),
    href=reverse_lazy('your-recently-resulted-list'),
    display='Your resulted',
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
        'js/rbhl/controllers/demographics_search.js',
        'js/rbhl/services/peak_flow_graph_data_loader.js',
        'js/rbhl/services/demographics_search_lookup.js',
        'js/rbhl/controllers/peak_flow_step.js',

    ]
    styles = [
        'css/rbhl.css'
    ]

    default_episode_category = OccupationalLungDiseaseEpisode.display_name

    @classmethod
    def get_menu_items(klass, user=None):
        # we import here as settings must be set before this is imported
        from rbhl.pathways import NewPatient, NewLabPatient

        if user:
            if user.is_authenticated:
                lab_user = user.profile.roles.filter(
                    name=constants.LAB_USER
                ).exists()

                if lab_user:
                    items = [
                        NewLabPatient.as_menuitem(
                            index=1,
                            display="New patient"
                        ),
                        menus.MenuItem(
                            activepattern=reverse('unresulted-list'),
                            href=reverse('unresulted-list'),
                            display=('Unresulted samples'),
                            icon="fa-table"
                        ),
                        menus.MenuItem(
                            activepattern=reverse(
                                'recently-recieved-samples-list'
                            ),
                            href=reverse('recently-recieved-samples-list'),
                            display=('Recent samples'),
                            icon="fa-table"
                        )
                    ]
                else:
                    items = [NewPatient.as_menuitem(index=1)]

                items.append(
                    menus.MenuItem(
                        activepattern=reverse('lab-overview'),
                        href=reverse('lab-overview'),
                        display=('Lab activity'),
                        icon="fa-bar-chart",
                        index=799
                    )
                )

                items.append(
                    menus.MenuItem(
                        activepattern=reverse('active-list'),
                        href=reverse('active-list'),
                        display=('Active patients'),
                        icon="fa-table"
                    )
                )
                today = datetime.date.today()
                year = today.year
                if today.month < 10:
                    year = year - 1
                items.append(
                    menus.MenuItem(
                        activepattern=reverse(
                            'clinic-activity-overview',
                            kwargs={"year": year}
                        ),
                        href=reverse('clinic-activity-overview', kwargs={"year": year}),
                        display=('Clinic activity'),
                        index=800,
                        icon="fa-bar-chart"
                    )
                )
                items.append(
                    menus.MenuItem(
                        activepattern=reverse_lazy('seen-by-me-list'),
                        href=reverse_lazy('seen-by-me-list'),
                        display='Seen by me',
                        icon="fa-table"
                    )
                )
                if your_recently_resulted.for_user(user):
                    items.append(your_recently_resulted)

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
