from django.contrib import admin
from django.utils.text import Truncator

from .models import AppointmentRequest, AppointmentStatusHistory, Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("name", "code")


class StatusHistoryInline(admin.TabularInline):
    model = AppointmentStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = ("from_status", "to_status", "note", "changed_by", "changed_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "booking_code", "full_name", "phone", "specialty", "symptoms_short", "requested_date",
        "status", "assigned_to", "created_at",
    )
    list_filter = ("status", "specialty", "requested_date", "created_at")
    search_fields = ("booking_code", "full_name", "phone_normalized", "symptoms")
    readonly_fields = (
        "id", "booking_code", "phone_normalized", "consent_version", "consent_at",
        "source", "idempotency_key", "created_at", "updated_at",
    )
    date_hierarchy = "requested_date"
    list_select_related = ("specialty", "assigned_to")
    inlines = (StatusHistoryInline,)

    @admin.display(description="Triệu chứng")
    def symptoms_short(self, obj):
        return Truncator(obj.symptoms).chars(60) if obj.symptoms else "—"

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = AppointmentRequest.objects.only("status").get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if previous_status != obj.status:
            AppointmentStatusHistory.objects.create(
                appointment=obj,
                from_status=previous_status or "",
                to_status=obj.status,
                changed_by=request.user,
            )


admin.site.site_header = "Quản trị website Bệnh viện"
admin.site.site_title = "Quản trị website"
admin.site.index_title = "Nội dung và đăng ký khám"
