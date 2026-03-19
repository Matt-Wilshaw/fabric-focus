"""Project middleware utilities."""

import traceback


class ExceptionLoggingMiddleware:
    """Log unhandled exceptions with request context to stdout/stderr."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
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
                },
            )
            print(traceback.format_exc())
            raise