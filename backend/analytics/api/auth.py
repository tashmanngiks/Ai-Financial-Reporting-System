"""Authentication endpoints."""

import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..views import login_view


@csrf_exempt
@require_http_methods(["GET", "POST"])
def simple_login_view(request):
    """Authenticate user and create a Django session for API requests."""
    if request.method == 'GET':
        return JsonResponse({'message': 'Login endpoint is accessible'})

    try:
        data = json.loads(request.body) if request.body else {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        login(request, user)
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': getattr(user, 'email', ''),
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
            },
        })
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)


__all__ = ['login_view', 'simple_login_view']
