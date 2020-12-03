from django.conf.urls import url
from legacy import views

urlpatterns = [
    url(
        r'^patient-lists/unresulted-list/$',
        views.UnresultedList.as_view(),
        name="unresulted-list"
    ),
    url(
        r'^patient-lists/your-recently-resulted-list/$',
        views.YourRecentlyResultedList.as_view(),
        name="your-recently-resulted-list"
    ),
    url(
        r'^lab-report/(?P<pk>\d+)/$',
        views.LabReport.as_view(),
        name="lab-report"
    )
]