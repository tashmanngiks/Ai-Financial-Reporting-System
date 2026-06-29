"""API authentication helpers."""

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth for SPA clients that do not send a CSRF header."""

    def enforce_csrf(self, request):
        return
