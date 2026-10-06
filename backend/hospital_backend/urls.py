from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("appointments.urls")),
    path("api/v1/news/", include("news.urls")),
    path("api/v1/dvkt/", include("dvkt.urls")),
    path("api/v1/chatbot/", include("chatbot.urls")),
    path("api/v1/zalo-bot/", include("zalo_bot.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

