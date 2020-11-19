from django.conf.urls import url
from legacy import views

urlpatterns = [
    url(
        r'^patient-lists/lab-work-list/$',
        views.LabWorkList.as_view(),
        name="lab-work-list"
    )
]
