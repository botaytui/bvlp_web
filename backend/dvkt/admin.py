from django.contrib import admin
from .models import Dvkt


@admin.register(Dvkt)
class DvktAdmin(admin.ModelAdmin):
    list_display = ("stt", "ma_dich_vu", "ten_dich_vu", "don_gia", "gia_thanh_toan", "tu_ngay", "den_ngay", "ma_cskcb")
    search_fields = ("ma_dich_vu", "ten_dich_vu", "ten_dvkt_gia")
    list_filter = ("ma_cskcb", "tu_ngay", "den_ngay")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 50
