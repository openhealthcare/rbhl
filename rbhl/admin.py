from django.contrib import admin
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.html import format_html
from two_factor.utils import default_device
from opal.admin import UserProfileAdmin


class RBHLUserAdmin(UserProfileAdmin):
    @property
    def list_display(self):
        return super().list_display + ("otp_setup",)

    def otp_setup(self, obj):
        if default_device(obj):
            # we can't just user method.boolean = True, because we want a setup OTP link
            return format_html("<img src='/assets/admin/img/icon-yes.svg' alt='True'>")
        else:
            url = reverse("two-factor-setup-redirect", kwargs={"username": obj.username})
            return format_html("<a href='{url}'>Set up OTP</a>", url=url)


admin.site.unregister(User)
admin.site.register(User, RBHLUserAdmin)
