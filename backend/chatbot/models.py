import json
from django.db import models


class ChatbotConfig(models.Model):
    is_enabled = models.BooleanField(
        "Bật Chatbot trên Website",
        default=True,
        help_text="Bật/Tắt hiển thị khung Chatbot trên toàn bộ website.",
    )
    bot_name = models.CharField(
        "Tên Trợ lý ảo",
        max_length=150,
        default="Trợ lý Y tế\nBệnh viện Lao và Bệnh phổi Bạc Liêu",
    )
    welcome_message = models.TextField(
        "Lời chào mở đầu",
        default=(
            "Xin chào! Tôi là Trợ lý AI Bệnh viện Lao và Bệnh phổi Bạc Liêu. "
            "Tôi có thể hỗ trợ bạn tra cứu lịch làm việc, thủ tục BHYT, triệu chứng hô hấp, "
            "hướng dẫn điều trị bệnh lao và bảng giá dịch vụ kỹ thuật."
        ),
    )
    emergency_hotline = models.CharField(
        "Hotline cấp cứu / Khẩn cấp",
        max_length=100,
        default="0291 3 678 977",
    )
    disclaimer_text = models.TextField(
        "Tuyên bố miễn trừ trách nhiệm y tế",
        default=(
            "Lưu ý y khoa: Thông tin do Trợ lý ảo cung cấp chỉ mang tính tham khảo và hướng dẫn thủ tục. "
            "Không thay thế cho việc khám bệnh, chẩn đoán và chỉ định điều trị trực tiếp từ Bác sĩ."
        ),
    )
    quick_prompts_json = models.TextField(
        "Danh sách gợi ý câu hỏi nhanh (JSON)",
        default=json.dumps(
            [
                "🕒 Giờ làm việc & Lịch khám",
                "💳 Khám BHYT cần giấy tờ gì?",
                "🩺 Triệu chứng nghi ngờ Lao phổi",
                "💰 Tra cứu giá X-quang & Xét nghiệm",
                "🩺 Khám Hen phế quản & COPD",
                "🚨 Dấu hiệu cấp cứu hô hấp",
            ],
            ensure_ascii=False,
            indent=2,
        ),
        help_text="Danh sách nút bấm câu hỏi nhanh cho người bệnh chọn.",
    )
    fallback_message = models.TextField(
        "Tin nhắn khi chưa tìm thấy câu trả lời",
        default=(
            "Dạ, câu hỏi của bạn cần được bác sĩ chuyên khoa tư vấn chi tiết hơn. "
            "Bạn có thể nhấn **Đặt lịch khám** hoặc gọi hotline **0291 3 678 977** để nhân viên y tế hỗ trợ bạn ngay nhé."
        ),
    )
    enable_ai = models.BooleanField(
        "Bật AI nâng cao (LLM)",
        default=False,
        help_text="Tùy chọn kết nối API AI nâng cao trong tương lai.",
    )
    ai_api_key = models.CharField(
        "API Key AI (nếu dùng)",
        max_length=255,
        blank=True,
    )
    updated_at = models.DateTimeField("Cập nhật lần cuối", auto_now=True)

    class Meta:
        db_table = "chatbot_config"
        verbose_name = "Cấu hình Chatbot"
        verbose_name_plural = "Cấu hình Chatbot"

    def __str__(self):
        status = "Đang BẬT" if self.is_enabled else "Đang TẮT"
        return f"{self.bot_name} ({status})"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    @property
    def quick_prompts_list(self):
        try:
            return json.loads(self.quick_prompts_json)
        except Exception:
            return [
                "🕒 Giờ làm việc & Lịch khám",
                "💳 Khám BHYT cần giấy tờ gì?",
                "🩺 Triệu chứng nghi ngờ Lao phổi",
                "💰 Tra cứu giá X-quang & Xét nghiệm",
            ]


class ChatbotFAQCategory(models.TextChoices):
    TIEP_DON = "TIEP_DON", "1. Đón tiếp & Giờ làm việc"
    BHYT = "BHYT", "2. BHYT & Chuyển tuyến"
    BENH_LAO = "BENH_LAO", "3. Bệnh Lao & CT Chống Lao"
    HO_HAP = "HO_HAP", "4. Bệnh Phổi - Hô hấp (Hen, COPD...)"
    DVKT_GIA = "DVKT_GIA", "5. Bảng giá dịch vụ & Xét nghiệm"
    CAP_CUU = "CAP_CUU", "6. Cấp cứu & Dấu hiệu nguy hiểm"
    TIEN_ICH = "TIEN_ICH", "7. Tiện ích & Liên hệ"


class ChatbotFAQ(models.Model):
    category = models.CharField(
        "Chuyên mục",
        max_length=50,
        choices=ChatbotFAQCategory.choices,
        default=ChatbotFAQCategory.TIEP_DON,
        db_index=True,
    )
    question = models.CharField("Câu hỏi / Vấn đề", max_length=500, db_index=True)
    answer = models.TextField("Nội dung trả lời chi tiết (Hỗ trợ Markdown)")
    keywords = models.TextField(
        "Từ khóa nhận diện (cách nhau bởi dấu phẩy)",
        blank=True,
        help_text="Ví dụ: gio kham, thoi gian, may gio mo cua, thu 7 co lam khong",
    )
    priority = models.IntegerField("Độ ưu tiên hiển thị", default=0)
    is_active = models.BooleanField("Kích hoạt", default=True, db_index=True)
    view_count = models.PositiveIntegerField("Lượt tra cứu", default=0)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật", auto_now=True)

    class Meta:
        db_table = "chatbot_faq"
        ordering = ["category", "-priority", "id"]
        verbose_name = "Câu hỏi & Tri thức Chatbot"
        verbose_name_plural = "Câu hỏi & Tri thức Chatbot"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.question}"


class ChatLog(models.Model):
    FEEDBACK_CHOICES = [
        ("none", "Chưa đánh giá"),
        ("like", "Hài lòng 👍"),
        ("dislike", "Chưa hài lòng 👎"),
    ]

    session_id = models.CharField("Mã phiên chat", max_length=100, db_index=True)
    user_message = models.TextField("Câu hỏi người dùng")
    bot_response = models.TextField("Phản hồi của Chatbot")
    matched_faq = models.ForeignKey(
        ChatbotFAQ,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_logs",
        verbose_name="FAQ tương ứng",
    )
    is_emergency = models.BooleanField("Dấu hiệu khẩn cấp", default=False)
    feedback = models.CharField(
        "Đánh giá của người dùng",
        max_length=20,
        choices=FEEDBACK_CHOICES,
        default="none",
    )
    ip_address = models.GenericIPAddressField("Địa chỉ IP", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    created_at = models.DateTimeField("Thời gian", auto_now_add=True, db_index=True)

    class Meta:
        db_table = "chatbot_chat_log"
        ordering = ["-created_at"]
        verbose_name = "Nhật ký hội thoại"
        verbose_name_plural = "Nhật ký hội thoại"

    def __str__(self):
        return f"[{self.created_at.strftime('%d/%m/%Y %H:%M')}] {self.user_message[:50]}..."
