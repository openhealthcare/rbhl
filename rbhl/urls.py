from django.conf.urls import include, url
from two_factor.urls import urlpatterns as tf_urls

from opal.urls import urlpatterns as opatterns
from opal import views as opal_views

from django.contrib import admin

admin.autodiscover()

from rbhl import views

urlpatterns = [
    url(r"", include(tf_urls)),
    # change the opal variable to have a name attribute
    url(r"^$", opal_views.IndexView.as_view(), name="home"),
    url(
        r"^change-password-check$",
        views.ChangePasswordCheck.as_view(),
        name="change-password-check",
    ),
    url(r"^import/", views.ImportView.as_view(), name="import"),
    url(
        r"^patient-lists/(?P<slug>[0-9a-z_\-]+)/?$",
        views.StaticTableListView.as_view(),
        name="static-list",
    ),
    url(r"^formsearch/", views.FormSearchRedirectView.as_view(), name="form-search"),
    url(r"^account/login/", views.TwoFactorRequired.as_view(), name="login"),
    url(
        r"^two-factor-required/",
        views.TwoFactorRequired.as_view(),
        name="two-factor-required",
    ),
    url(
        r"^two-factor-setup/",
        views.TwoFactorSetupView.as_view(),
        name="two-factor-setup",
    ),
    url(
        r"^account/two_factor/(?P<username>[0-9A-Za-z_\-]+)/setup",
        views.OtpSetupRelogin.as_view(),
        name="two-factor-setup-redirect",
    ),
]

urlpatterns = opatterns + urlpatterns
