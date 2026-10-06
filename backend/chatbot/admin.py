from django.contrib import admin
from django.utils.html import format_html
from .models import ChatbotConfig, ChatbotFAQ, ChatLog


@admin.register(ChatbotConfig)
class ChatbotConfigAdmin(admin.ModelAdmin):
    list_display = ("bot_name", "status_badge", "emergency_hotline", "updated_at")
    fieldsets = (
        (
            "Trạng thái hoạt động",
            {
                "fields": ("is_enabled", "bot_name"),
                "description": "Bật hoặc Tắt Chatbot hiển thị trên giao diện người dùng website.",
            },
        ),
        (
            "Nội dung & Lời chào",
            {
                "fields": (
                    "welcome_message",
                    "emergency_hotline",
                    "disclaimer_text",
                    "fallback_message",
                    "quick_prompts_json",
                ),
            },
        ),
        (
            "Cấu hình AI nâng cao (Tùy chọn tương lai)",
            {
                "fields": ("enable_ai", "ai_api_key"),
                "classes": ("collapse",),
            },
        ),
    )

    def status_badge(self, obj):
        if obj.is_enabled:
            return format_html(
                '<span style="background-color:#2e7d32; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">● ĐANG BẬT</span>'
            )
        return format_html(
            '<span style="background-color:#c62828; color:#fff; padding:4px 8px; border-radius:4px; font-weight:bold;">○ ĐANG TẮT</span>'
        )

    status_badge.short_description = "Trạng thái"

    def has_add_permission(self, request):
        # Only allow 1 singleton config
        return not ChatbotConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "category_badge",
        "priority",
        "is_active",
        "view_count",
        "updated_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("question", "answer", "keywords")
    list_editable = ("priority", "is_active")
    ordering = ("category", "-priority", "id")

    fieldsets = (
        (
            "Nội dung câu hỏi & Trả lời",
            {
                "fields": ("category", "question", "answer", "keywords"),
            },
        ),
        (
            "Cấu hình hiển thị",
            {
                "fields": ("priority", "is_active", "view_count"),
            },
        ),
    )

    def category_badge(self, obj):
        colors = {
            "TIEP_DON": "#0288d1",
            "BHYT": "#7b1fa2",
            "BENH_LAO": "#d32f2f",
            "HO_HAP": "#00796b",
            "DVKT_GIA": "#f57c00",
            "CAP_CUU": "#c2185b",
            "TIEN_ICH": "#455a64",
        }
        color = colors.get(obj.category, "#555")
        return format_html(
            '<span style="background-color:{}; color:#fff; padding:3px 6px; border-radius:3px; font-size:11px;">{}</span>',
            color,
            obj.get_category_display(),
        )

    category_badge.short_description = "Chuyên mục"


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user_message_short",
        "matched_faq_display",
        "emergency_badge",
        "feedback_badge",
        "session_id",
    )
    list_filter = ("is_emergency", "feedback", "created_at")
    search_fields = ("user_message", "bot_response", "session_id", "ip_address")
    readonly_fields = (
        "session_id",
        "user_message",
        "bot_response",
        "matched_faq",
        "is_emergency",
        "feedback",
        "ip_address",
        "user_agent",
        "created_at",
    )

    def user_message_short(self, obj):
        return obj.user_message[:60] + ("..." if len(obj.user_message) > 60 else "")

    user_message_short.short_description = "Câu hỏi người dùng"

    def matched_faq_display(self, obj):
        if obj.matched_faq:
            return obj.matched_faq.question[:40]
        return "-"

    matched_faq_display.short_description = "Khớp với FAQ"

    def emergency_badge(self, obj):
        if obj.is_emergency:
            return format_html(
                '<span style="background-color:#d32f2f; color:#fff; padding:2px 6px; border-radius:3px; font-weight:bold;">🚨 KHẨN CẤP</span>'
            )
        return "Bình thường"

    emergency_badge.short_description = "Cấp cứu"

    def feedback_badge(self, obj):
        if obj.feedback == "like":
            return format_html('<span style="color:#2e7d32; font-weight:bold;">👍 Hài lòng</span>')
        elif obj.feedback == "dislike":
            return format_html('<span style="color:#c62828; font-weight:bold;">👎 Chưa hài lòng</span>')
        return "Chưa đánh giá"

    feedback_badge.short_description = "Đánh giá"

    def has_add_permission(self, request):
        return False
