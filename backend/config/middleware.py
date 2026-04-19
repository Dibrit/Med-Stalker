import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Tiny request logger.

    This is mainly for local debugging so I can see what the frontend is doing
    without setting up anything fancy (and the timing is useful when something
    feels slow).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000

        user = getattr(request, "user", None)
        user_id = user.pk if user is not None and getattr(user, "is_authenticated", False) else None

        message = "%s %s -> %s (%.2fms) user_id=%s"
        args = (request.method, request.path, response.status_code, duration_ms, user_id)

        if response.status_code >= 500:
            logger.error(message, *args)
        elif response.status_code >= 400:
            logger.warning(message, *args)
        else:
            logger.info(message, *args)

        return response
