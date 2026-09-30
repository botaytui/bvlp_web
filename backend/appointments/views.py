import json
import re
from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import AppointmentRequest, AppointmentStatusHistory, Specialty


PHONE_PATTERN = re.compile(r"^(?:0|\+84)(\d{9})$")


def api_error(message, status=400, field_errors=None):
    payload = {"success": False, "message": message}
    if field_errors:
        payload["errors"] = field_errors
    return JsonResponse(payload, status=status)


def normalize_phone(value):
    compact = re.sub(r"[\s.()-]", "", str(value or ""))
    match = PHONE_PATTERN.fullmatch(compact)
    if not match:
        return None
    return "0" + match.group(1)


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "service": "hospital-booking-api"})


@require_GET
def specialties(request):
    items = Specialty.objects.filter(is_active=True).values("code", "name")
    return JsonResponse({"success": True, "items": list(items)})


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def create_appointment(request):
    if request.method == "OPTIONS":
        return JsonResponse({}, status=204)

    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return api_error("Dữ liệu gửi lên không hợp lệ.")

    if payload.get("website"):
        return api_error("Không thể tiếp nhận đăng ký.")

    full_name = " ".join(str(payload.get("fullName", "")).split())
    phone = normalize_phone(payload.get("phone"))
    specialty_code = str(payload.get("specialty", "")).strip()
    symptoms = str(payload.get("symptoms", "")).strip()
    requested_date_raw = str(payload.get("appointmentDate", "")).strip()
    consent = payload.get("consent") is True
    idempotency_key = str(payload.get("idempotencyKey", "")).strip()[:64] or None

    errors = {}
    if len(full_name) < 2 or len(full_name) > 120:
        errors["fullName"] = "Họ và tên phải có từ 2 đến 120 ký tự."
    if not phone:
        errors["phone"] = "Số điện thoại Việt Nam không hợp lệ."
    if not consent:
        errors["consent"] = "Cần đồng ý để bệnh viện tiếp nhận đăng ký."
    if len(symptoms) > 1500:
        errors["symptoms"] = "Mô tả triệu chứng không được vượt quá 1.500 ký tự."

    try:
        requested_date = date.fromisoformat(requested_date_raw)
    except ValueError:
        requested_date = None
        errors["appointmentDate"] = "Ngày khám không hợp lệ."

    today = timezone.localdate()
    if requested_date and not today <= requested_date <= today + timedelta(days=90):
        errors["appointmentDate"] = "Ngày khám phải nằm trong 90 ngày tới."

    specialty = None
    if specialty_code:
        try:
            specialty = Specialty.objects.get(code=specialty_code, is_active=True)
        except Specialty.DoesNotExist:
            errors["specialty"] = "Chuyên khoa không hợp lệ hoặc đang ngừng nhận lịch."

    if not specialty_code and not symptoms:
        message = "Vui lòng chọn chuyên khoa hoặc mô tả triệu chứng."
        errors["specialty"] = message
        errors["symptoms"] = message

    if errors:
        return api_error("Vui lòng kiểm tra lại thông tin.", field_errors=errors)

    if idempotency_key:
        existing = AppointmentRequest.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return JsonResponse({
                "success": True,
                "duplicate": True,
                "bookingCode": existing.booking_code,
                "message": "Đăng ký đã được tiếp nhận trước đó.",
            })

    active_statuses = [
        AppointmentRequest.Status.NEW,
        AppointmentRequest.Status.CONTACTED,
        AppointmentRequest.Status.CONFIRMED,
    ]
    duplicate_filter = {
        "phone_normalized": phone,
        "specialty": specialty,
        "requested_date": requested_date,
        "status__in": active_statuses,
    }
    existing = AppointmentRequest.objects.filter(**duplicate_filter).first()
    if existing:
        return JsonResponse({
            "success": True,
            "duplicate": True,
            "bookingCode": existing.booking_code,
            "message": "Lịch đăng ký này đã được tiếp nhận.",
        })

    try:
        with transaction.atomic():
            appointment = AppointmentRequest.objects.create(
                full_name=full_name,
                phone=phone,
                phone_normalized=phone,
                symptoms=symptoms,
                specialty=specialty,
                requested_date=requested_date,
                consent_at=timezone.now(),
                consent_version="booking-v1",
                idempotency_key=idempotency_key,
            )
            AppointmentStatusHistory.objects.create(
                appointment=appointment,
                to_status=AppointmentRequest.Status.NEW,
                note="Tiếp nhận từ website",
            )
    except IntegrityError:
        existing = AppointmentRequest.objects.filter(**duplicate_filter).first()
        if not existing and idempotency_key:
            existing = AppointmentRequest.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return JsonResponse({
                "success": True,
                "duplicate": True,
                "bookingCode": existing.booking_code,
                "message": "Đăng ký đã được tiếp nhận trước đó.",
            })
        return api_error("Chưa thể lưu đăng ký. Vui lòng thử lại.", status=409)

    return JsonResponse({
        "success": True,
        "bookingCode": appointment.booking_code,
        "message": "Bệnh viện đã tiếp nhận thông tin đăng ký.",
    }, status=201)
