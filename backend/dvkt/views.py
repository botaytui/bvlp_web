from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Dvkt


@require_GET
def service_prices(request):
    services = Dvkt.objects.order_by("stt", "ma_dich_vu", "pk").values(
        "stt", "ma_dich_vu", "ten_dvkt_gia", "don_gia"
    )
    items = [
        {
            "stt": item["stt"],
            "ma_dich_vu": item["ma_dich_vu"][:12],
            "ten_dich_vu": item["ten_dvkt_gia"],
            "don_gia": str(item["don_gia"]) if item["don_gia"] is not None else None,
        }
        for item in services
    ]
    return JsonResponse({"success": True, "count": len(items), "items": items})
