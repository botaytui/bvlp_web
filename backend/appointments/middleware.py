from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class CorsMiddleware:
    """CORS tối thiểu, chỉ mở cho các origin được cấu hình rõ ràng."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allowed = (
            origin in settings.CORS_ALLOWED_ORIGINS
            or (origin and (
                origin.startswith("http://localhost:")
                or origin.startswith("http://127.0.0.1:")
                or "zdn.vn" in origin
                or "zalo.me" in origin
                or "zaloplatforms.com" in origin
            ))
        )
        if request.method == "OPTIONS" and allowed:
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Max-Age"] = "86400"
            patch_vary_headers(response, ("Origin",))
        return response
