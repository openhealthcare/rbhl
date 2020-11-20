from django.conf.urls import url
from legacy import views

urlpatterns = [
    url(
        r'^patient-lists/unresulted-list/$',
        views.UnresultedList.as_view(),
        name="unresulted-list"
    )
]
