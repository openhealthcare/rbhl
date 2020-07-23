from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from two_factor.utils import default_device
from opal.admin import UserProfileAdmin
from rbhl.models import SetUpTwoFactor


def enable_otp_setup(modeladmin, request, queryset):
    disable_otp(modeladmin, request, queryset)
    for user in queryset:
        SetUpTwoFactor.objects.create(user=user)


enable_otp_setup.short_description = "Enable OTP setup"


def disable_otp(modeladmin, request, queryset):
    SetUpTwoFactor.objects.filter(user__in=queryset).delete()
    for user in queryset:
        dd = default_device(user)
        if dd:
            dd.delete()


disable_otp.short_description = "Disable OTP"


class RBHLUserAdmin(UserProfileAdmin):
    actions = [enable_otp_setup, disable_otp]

    @property
    def list_display(self):
        return super().list_display + ("otp_status",)

    def otp_status(self, obj):
        if default_device(obj):
            # we can't just user method.boolean = True,
            # because we want a setup OTP link
            return format_html(
                "<img src='/assets/admin/img/icon-yes.svg' alt='True'>"
            )
        else:
            time_left = SetUpTwoFactor.time_left(obj)
            if time_left:
                return "Waiting for user ({} minutes left)".format(time_left)
            else:
                return format_html(
                    "<img src='/assets/admin/img/icon-no.svg' alt='False'>"
                )


admin.site.unregister(User)
admin.site.register(User, RBHLUserAdmin)
