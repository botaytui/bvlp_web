import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatbotConfig, ChatbotFAQ, ChatLog
from .services import process_user_chat


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@require_http_methods(["GET"])
def chatbot_config_api(request):
    """API endpoint to get Chatbot configuration and status."""
    config = ChatbotConfig.get_solo()
    data = {
        "is_enabled": config.is_enabled,
        "bot_name": config.bot_name,
        "welcome_message": config.welcome_message,
        "emergency_hotline": config.emergency_hotline,
        "disclaimer_text": config.disclaimer_text,
        "quick_prompts": config.quick_prompts_list,
    }
    return JsonResponse({"success": True, "data": data})


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_chat_api(request):
    """API endpoint to handle user messages."""
    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    user_message = body.get("message", "").strip()
    session_id = body.get("session_id", "").strip() or "anonymous"

    if not user_message:
        return JsonResponse(
            {"success": False, "message": "Vui lòng nhập nội dung câu hỏi."},
            status=400,
        )

    config = ChatbotConfig.get_solo()
    if not config.is_enabled:
        return JsonResponse(
            {
                "success": False,
                "disabled": True,
                "message": "Chatbot hiện đang tạm tắt trên hệ thống.",
            },
            status=403,
        )

    result = process_user_chat(user_message, session_id=session_id)

    # Save to ChatLog
    try:
        matched_faq = None
        if result.get("matched_faq_id"):
            matched_faq = ChatbotFAQ.objects.filter(id=result["matched_faq_id"]).first()

        chat_log = ChatLog.objects.create(
            session_id=session_id,
            user_message=user_message,
            bot_response=result.get("reply", ""),
            matched_faq=matched_faq,
            is_emergency=result.get("is_emergency", False),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        result["log_id"] = chat_log.id
    except Exception as e:
        # Logging failure shouldn't fail the user request
        pass

    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_feedback_api(request):
    """API endpoint to record user satisfaction feedback."""
    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    log_id = body.get("log_id")
    feedback = body.get("feedback", "none")

    if feedback not in ["like", "dislike"]:
        return JsonResponse({"success": False, "message": "Đánh giá không hợp lệ."}, status=400)

    if log_id:
        ChatLog.objects.filter(id=log_id).update(feedback=feedback)
        return JsonResponse({"success": True, "message": "Cảm ơn bạn đã gửi đánh giá!"})

    return JsonResponse({"success": False, "message": "Không tìm thấy phiên chat."}, status=404)
