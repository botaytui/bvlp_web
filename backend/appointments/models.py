import secrets
import string
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


def generate_booking_code():
    alphabet = string.ascii_uppercase + string.digits
    return "DL-" + "".join(secrets.choice(alphabet) for _ in range(8))


class Specialty(models.Model):
    code = models.SlugField("Mã", max_length=50, unique=True)
    name = models.CharField("Tên chuyên khoa", max_length=120, unique=True)
    is_active = models.BooleanField("Đang nhận lịch", default=True)
    sort_order = models.PositiveSmallIntegerField("Thứ tự", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Chuyên khoa"
        verbose_name_plural = "Chuyên khoa"

    def __str__(self):
        return self.name


class AppointmentRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Mới tiếp nhận"
        CONTACTED = "contacted", "Đã liên hệ"
        CONFIRMED = "confirmed", "Đã xác nhận"
        COMPLETED = "completed", "Đã hoàn thành"
        CANCELLED = "cancelled", "Đã hủy"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_code = models.CharField(
        "Mã đăng ký", max_length=11, unique=True, default=generate_booking_code, editable=False
    )
    full_name = models.CharField("Họ và tên", max_length=120)
    phone = models.CharField("Số điện thoại", max_length=20)
    phone_normalized = models.CharField("Số điện thoại chuẩn hóa", max_length=11, db_index=True)
    symptoms = models.TextField("Mô tả triệu chứng", max_length=1500, blank=True)
    specialty = models.ForeignKey(
        Specialty,
        verbose_name="Chuyên khoa",
        on_delete=models.PROTECT,
        related_name="appointments",
        null=True,
        blank=True,
    )
    requested_date = models.DateField("Ngày mong muốn", db_index=True)
    status = models.CharField(
        "Trạng thái", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    consent_version = models.CharField("Phiên bản đồng ý", max_length=30, default="booking-v1")
    consent_at = models.DateTimeField("Thời điểm đồng ý")
    source = models.CharField("Nguồn", max_length=30, default="website")
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True, editable=False)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Người xử lý",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )
    internal_note = models.TextField("Ghi chú nội bộ", blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Cập nhật", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Đăng ký khám"
        verbose_name_plural = "Đăng ký khám"
        indexes = [
            models.Index(fields=["status", "requested_date"], name="appt_status_date_idx"),
            models.Index(fields=["specialty", "requested_date"], name="appt_spec_date_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["phone_normalized", "specialty", "requested_date"],
                condition=Q(status__in=["new", "contacted", "confirmed"]),
                name="unique_active_appointment",
                nulls_distinct=False,
            )
        ]

    def __str__(self):
        return f"{self.booking_code} - {self.full_name}"


class AppointmentStatusHistory(models.Model):
    appointment = models.ForeignKey(
        AppointmentRequest, on_delete=models.CASCADE, related_name="status_history"
    )
    from_status = models.CharField("Từ trạng thái", max_length=20, blank=True)
    to_status = models.CharField("Đến trạng thái", max_length=20)
    note = models.TextField("Ghi chú", blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    changed_at = models.DateTimeField("Thời điểm", auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "Lịch sử trạng thái"
        verbose_name_plural = "Lịch sử trạng thái"
