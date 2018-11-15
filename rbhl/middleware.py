

class SecurityHeadersMiddleware:

    def process_request(self, request):
        request.META['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
        request.META['Content-Security-Policy-Report-Only'] = "script-src self"
        request.META['X-Frame-Options'] = "SAMEORIGIN"
        request.META['X-XSS-Protection'] = "1; mode=block"
        request.META['X-Content-Type-Options'] = "nosniff"
        request.META['Referrer-Policy'] = 'same-origin'
