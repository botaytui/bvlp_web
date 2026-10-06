import hmac
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .config import configuration
from .core import Engine
from .gateway import Queue, process_event


def price_rows():
    from dvkt.models import Dvkt
    return [{'ma_dich_vu':x['ma_dich_vu'], 'ten_dich_vu':x['ten_dvkt_gia'] or x['ten_dich_vu'],
             'don_gia':x['don_gia']} for x in Dvkt.objects.values('ma_dich_vu','ten_dvkt_gia','ten_dich_vu','don_gia')]


engine = Engine(price_rows)


@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        return JsonResponse({'service':'hospital-zalo-bot', 'configured':bool(configuration()['secret']), 'mode':'pilot'})
    if request.method != 'POST':
        return JsonResponse({'error':'method'}, status=405)
    config = configuration()
    if len(config['secret']) < 8 or not config['token']:
        return JsonResponse({'error':'not_configured'}, status=503)
    given = request.headers.get('X-Bot-Api-Secret-Token', '')
    if not hmac.compare_digest(given.encode(), config['secret'].encode()):
        return JsonResponse({'error':'unauthorized'}, status=403)
    if len(request.body) > 16384:
        return JsonResponse({'error':'payload_too_large'}, status=413)
    try:
        payload = json.loads(request.body)
        if not isinstance(payload, dict):
            raise ValueError()
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'error':'invalid_json'}, status=400)
    try:
        status = process_event(payload, config, engine, Queue())
    except Exception:
        # No raw payload, credentials or chat IDs in errors.
        return JsonResponse({'error':'queue_unavailable'}, status=503)
    if status == 'full':
        return JsonResponse({'error':'queue_full'}, status=503)
    # Authenticated verification/unsupported events are acknowledged without sending.
    return JsonResponse({'ok':True, 'status':status})
