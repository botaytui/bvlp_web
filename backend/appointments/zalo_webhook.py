"""Receive signed Zalo Mini App events without reading or modifying patient records."""
import hashlib
import hmac
import json
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def generate_signature(data, api_key):
    def value_text(value):
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    content = "".join(value_text(data[key]) for key in sorted(data)) + api_key
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    if request.method == "GET":
        return JsonResponse({"status": "ok", "service": "hospital-zalo-miniapp-webhook"})
    if len(request.body) > 16384:
        return JsonResponse({"error": "payload_too_large"}, status=413)
    api_key = settings.ZALO_MINIAPP_API_KEY
    if not api_key:
        return JsonResponse({"error": "webhook_not_configured"}, status=503)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid_json"}, status=400)
    if not isinstance(data, dict) or not all(isinstance(k, str) for k in data):
        return JsonResponse({"error": "invalid_payload"}, status=400)
    supplied = request.headers.get("X-ZEvent-Signature", "")
    if len(supplied) != 64 or any(c not in "0123456789abcdef" for c in supplied) or not hmac.compare_digest(generate_signature(data, api_key), supplied):
        return JsonResponse({"error": "invalid_signature"}, status=403)
    if str(data.get("appId", "")) != settings.ZALO_MINIAPP_ID:
        return JsonResponse({"error": "unknown_app"}, status=403)
    event = data.get("event")
    if not isinstance(event, str) or len(event) > 100:
        return JsonResponse({"error": "invalid_event"}, status=400)
    if event == "user.revoke.consent" and (not isinstance(data.get("userId"), str) or not data["userId"]):
        return JsonResponse({"error": "invalid_user"}, status=400)
    # An idempotent receipt contains no raw user identifier or medical data.
    event_id = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    receipt = {"event": event, "appId": settings.ZALO_MINIAPP_ID,
               "timestamp": data.get("timestamp"), "received": True}
    if event == "user.revoke.consent":
        # Booking requests use manually entered contact details, not Zalo User ID.
        # Do not delete somebody's booking by an unverified identifier mapping.
        receipt["result"] = "no_zalo_account_profile_stored"
    elif event == "versions.review.done":
        receipt.update({"versionId": data.get("versionId"), "status": data.get("status")})
    folder = Path(settings.ZALO_MINIAPP_EVENT_DIR)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / (event_id + ".json")).open("x", encoding="utf-8") as handle:
            json.dump(receipt, handle, ensure_ascii=False)
    except FileExistsError:
        pass
    except OSError:
        return JsonResponse({"error": "receipt_storage_unavailable"}, status=503)
    return JsonResponse({"success": True})
