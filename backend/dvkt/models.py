from django.db import models


class Dvkt(models.Model):
    stt = models.PositiveIntegerField("STT", null=True, blank=True)
    ma_dich_vu = models.CharField("Mã dịch vụ", max_length=100, db_index=True)
    ten_dich_vu = models.TextField("Tên dịch vụ")
    ten_dvkt_gia = models.TextField("Tên DVKT theo giá", blank=True)
    don_gia = models.DecimalField("Đơn giá", max_digits=20, decimal_places=4, null=True, blank=True)
    quy_trinh = models.TextField("Quy trình", blank=True)
    so_luong_cgkt = models.PositiveIntegerField("Số lượng chuyển giao kỹ thuật", null=True, blank=True)
    cskcb_cgkt = models.CharField("CSKCB chuyển giao kỹ thuật", max_length=255, blank=True)
    cskcb_cls = models.CharField("CSKCB cận lâm sàng", max_length=255, blank=True)
    qd_dvkt = models.TextField("Quyết định DVKT", blank=True)
    qd_pd_gia = models.TextField("Quyết định phê duyệt giá", blank=True)
    ghi_chu = models.TextField("Ghi chú", blank=True)
    ma_thuoc = models.CharField("Mã thuốc", max_length=255, blank=True)
    ten_thuoc = models.TextField("Tên thuốc", blank=True)
    so_dang_ky = models.CharField("Số đăng ký", max_length=255, blank=True)
    don_vi_tinh = models.CharField("Đơn vị tính", max_length=100, blank=True)
    tt_thau = models.TextField("Thông tin thầu", blank=True)
    don_gia_thuoc = models.DecimalField("Đơn giá thuốc", max_digits=20, decimal_places=4, null=True, blank=True)
    dm_nsx_cdd = models.DecimalField("Định mức NSX CDD", max_digits=20, decimal_places=6, null=True, blank=True)
    dm_thucte_cdd = models.DecimalField("Định mức thực tế CDD", max_digits=20, decimal_places=6, null=True, blank=True)
    lieu_bq_px = models.DecimalField("Liều BQ PX", max_digits=20, decimal_places=6, null=True, blank=True)
    tl_thucte_bq_px = models.DecimalField("Tỷ lệ thực tế BQ PX", max_digits=20, decimal_places=6, null=True, blank=True)
    thanh_tien_thuoc = models.DecimalField("Thành tiền thuốc", max_digits=20, decimal_places=4, null=True, blank=True)
    gia_thanh_toan = models.DecimalField("Giá thanh toán", max_digits=20, decimal_places=4, null=True, blank=True)
    tu_ngay = models.DateField("Từ ngày")
    den_ngay = models.DateField("Đến ngày", null=True, blank=True)
    ma_cskcb = models.CharField("Mã CSKCB", max_length=20, db_index=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật", auto_now=True)

    class Meta:
        db_table = "dvkt"
        ordering = ["stt", "ma_dich_vu"]
        verbose_name = "Dịch vụ kỹ thuật"
        verbose_name_plural = "Dịch vụ kỹ thuật"
        constraints = [
            models.UniqueConstraint(fields=["ma_cskcb", "ma_dich_vu", "tu_ngay"], name="dvkt_unique_service_date"),
            models.CheckConstraint(condition=models.Q(den_ngay__isnull=True) | models.Q(den_ngay__gte=models.F("tu_ngay")), name="dvkt_valid_date_range"),
        ]

    def __str__(self):
        return f"{self.ma_dich_vu} - {self.ten_dich_vu}"
