class SecurityHeadersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"
        response['Content-Security-Policy-Report-Only'] = "script-src self"
        response['X-Frame-Options'] = "SAMEORIGIN"
        response['X-XSS-Protection'] = "1; mode=block"
        response['X-Content-Type-Options'] = "nosniff"
        response['Referrer-Policy'] = 'same-origin'

        return response
