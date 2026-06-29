"""Project middleware."""


class Utf8JsonContentTypeMiddleware:
    """Ensure JSON API responses declare UTF-8 charset."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if content_type.startswith('application/json') and 'charset=' not in content_type.lower():
            response['Content-Type'] = 'application/json; charset=utf-8'
        return response


class SecurityHeaderCleanupMiddleware:
    """Normalize headers to reduce noisy audit warnings."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prefer explicit CSP frame-ancestors instead of legacy X-Frame-Options.
        response['Content-Security-Policy'] = "frame-ancestors 'none'"

        for header in ('X-XSS-Protection', 'X-Frame-Options', 'Expires'):
            if header in response:
                del response[header]

        return response
