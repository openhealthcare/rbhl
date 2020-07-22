import logging
from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, reverse
from django.contrib.auth import logout
from two_factor.utils import default_device
from rbhl.models import SetUpTwoFactor


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response[
            'Strict-Transport-Security'
        ] = "max-age=31536000; includeSubDomains"
        response['Content-Security-Policy-Report-Only'] = "script-src self"
        response['X-Frame-Options'] = "SAMEORIGIN"
        response['X-XSS-Protection'] = "1; mode=block"
        response['X-Content-Type-Options'] = "nosniff"
        response['Referrer-Policy'] = 'same-origin'
        return response


class TwoStageAuthenticationRequired(MiddlewareMixin):
    def process_request(self, request):
        """
            Five possible outcomes

            1. The view is not login required.
               - just return, nothing to see here
            2. The user is authenticated and verified,
               - great you're good to go
            3. The user is authenticated but does not have two factor
               auth set up
               - log out the user and redirect them requesting them to
                 contact us
            4. The user is authenticated and is not verified
               - redirect to do 2 step auth
            5. The user is not authenticated
               - redirect to log in

            We don't use the the two factor auth inital log in, to put them
            through the standard opal authentication first.
        """
        resolved_match = resolve(request.path_info)
        for url_name in settings.LOGIN_NOT_REQUIRED:
            name_space = None
            if isinstance(url_name, tuple):
                url_name, name_space = url_name
            if resolved_match.url_name == url_name:
                if name_space:
                    if name_space in resolved_match.namespaces:
                        return
                else:
                    return

        if request.user.is_authenticated:
            if not settings.TWO_FACTOR_FOR_SUPERUSERS:
                if request.user.is_superuser:
                    return
            if request.user.is_verified():
                return
            elif default_device(request.user):
                return redirect("two-factor-login")
            elif SetUpTwoFactor.allowed(request.user):
                return redirect("two-factor-setup")
            else:
                logging.error(
                    "user {} has not had two factor auth set up".format(
                        request.user.username
                    )
                )
                logout(request)
                return redirect("two-factor-required")

        return redirect(reverse("two_factor:login"))
