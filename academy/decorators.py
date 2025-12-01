from django.core.cache import cache
from django.http import HttpResponse
from functools import wraps
import time

def rate_limit(limit=5, period=60):
    """
    Simple rate limiting decorator using Django cache.
    limit: Max requests allowed
    period: Time window in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Only limit POST requests usually, but can be configured.
            # For login/payment, we definitely want to limit POST.
            if request.method != 'POST':
                return view_func(request, *args, **kwargs)

            # Identify client: User ID if logged in, else IP
            if request.user.is_authenticated:
                ident = f"user_{request.user.id}"
            else:
                ident = f"ip_{get_client_ip(request)}"

            # Create a unique cache key based on view name and identity
            key = f"rate_limit_{view_func.__name__}_{ident}"

            # Get current history
            history = cache.get(key, [])
            now = time.time()

            # Filter out timestamps older than the period
            history = [t for t in history if now - t < period]

            if len(history) >= limit:
                return HttpResponse("Too Many Requests. Please try again later.", status=429)

            # Add current timestamp
            history.append(now)
            cache.set(key, history, period + 10) # Set expiry slightly longer than period

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
