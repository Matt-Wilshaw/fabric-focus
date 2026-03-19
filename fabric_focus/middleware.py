"""Project middleware utilities."""

import traceback
from django.utils.deprecation import MiddlewareMixin


class ExceptionLoggingMiddleware(MiddlewareMixin):
    """Log unhandled exceptions with request context to stdout/stderr."""

    def process_exception(self, request, exception):
        bag = None
        try:
            bag = request.session.get('bag', {})
        except Exception:
            bag = '<unavailable>'

        print(
            'UNHANDLED_EXCEPTION',
            {
                'method': request.method,
                'path': request.path,
                'bag_type': type(bag).__name__,
                'bag_preview': str(bag)[:500],
                'error_type': type(exception).__name__,
                'error': str(exception),
            },
        )
        print(traceback.format_exc())
        return None