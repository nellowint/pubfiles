from functools import wraps

from django.core.cache import cache


def rate_limit(key_prefix, max_attempts=3, timeout=3600, methods=('POST',)):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            request.limited = False
            if request.method not in methods:
                return view_func(request, *args, **kwargs)

            ip = request.META.get(
                'HTTP_X_FORWARDED_FOR',
                request.META.get('REMOTE_ADDR', ''),
            ).split(',')[0].strip()

            cache_key = f'{key_prefix}:{ip}'
            attempts = cache.get(cache_key, 0)

            request.limited = attempts >= max_attempts

            if not request.limited:
                cache.set(cache_key, attempts + 1, timeout)

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
