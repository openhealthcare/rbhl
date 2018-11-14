from django.conf.urls import include, url

from opal.urls import urlpatterns as opatterns

from django.contrib import admin
admin.autodiscover()

from rbhl import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^import/', views.ImportView.as_view(), name='import'),
    url(r'^patient-lists/(?P<slug>[0-9a-z_\-]+)/?$',
        views.StaticTableListView.as_view(), name='static-list'),
    url(r'^formsearch/', views.FormSearchRedirectView.as_view(),
        name='form-search'),
]

urlpatterns += opatterns
