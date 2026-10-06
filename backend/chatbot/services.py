import re
import unicodedata
from django.db.models import Q
from .models import ChatbotConfig, ChatbotFAQ, ChatbotFAQCategory
from dvkt.models import Dvkt


def remove_accents(input_str: str) -> str:
    """Remove Vietnamese accents for accent-insensitive matching."""
    if not input_str:
        return ""
    # Normalize unicode to decomposed form
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    # Filter out diacritics
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Special case for Vietnamese 'đ' / 'Đ'
    return only_ascii.replace("đ", "d").replace("Đ", "d").lower().strip()


def tokenize(text: str) -> set:
    """Tokenize normalized text into clean alphanumeric words."""
    cleaned = re.sub(r"[^\w\s]", " ", remove_accents(text))
    return {w for w in cleaned.split() if len(w) > 1}


# --------------------------------------------------------------------------
# Red Flag & Emergency Respiratory Detection
# --------------------------------------------------------------------------
EMERGENCY_PATTERNS = [
    r"\bho ra mau\b",
    r"\bkhac ra mau\b",
    r"\boi ra mau\b",
    r"\bnon ra mau\b",
    r"\bkho tho du doi\b",
    r"\bkhong tho duoc\b",
    r"\bngat tho\b",
    r"\btim tai\b",
    r"\bsuy ho hap\b",
    r"\bdau nguc du doi\b",
    r"\bhon me\b",
    r"\bbat tinh\b",
    r"\bco giat\b",
    r"\bsot cao co giat\b",
]


def check_emergency(user_message: str) -> bool:
    norm = remove_accents(user_message)
    for pat in EMERGENCY_PATTERNS:
        if re.search(pat, norm):
            return True
    return False


def get_emergency_response(config: ChatbotConfig) -> dict:
    hotline = config.emergency_hotline or "0291 3 678 977"
    text = (
        f"🚨 **CẢNH BÁO Y TẾ KHẨN CẤP** 🚨\n\n"
        f"Hệ thống ghi nhận triệu chứng nguy hiểm đường hô hấp (như ho ra máu, khó thở dữ dội, đau ngực cấp...).\n\n"
        f"**HÀNH ĐỘNG NGAY:**\n"
        f"1. **Gọi cấp cứu 115** hoặc Hotline Cấp cứu BV Lao & Bệnh Phổi Bạc Liêu: **[{hotline}](tel:{hotline.replace(' ', '').replace('/', ',')})**.\n"
        f"2. **Tư thế người bệnh:** Cho người bệnh nằm nghỉ ở tư thế nửa nằm nửa ngồi hoặc nằm nghiêng về bên nghi tổn thương, nới lỏng cổ áo, giữ đường thở thông thoáng.\n"
        f"3. **Lưu ý quan trọng:** Động viên người bệnh ho nhẹ tống máu/đờm ra ngoài, **tuyệt đối không nuốt máu**, không tự ý uống thuốc cầm máu khi chưa có chỉ định của bác sĩ.\n"
        f"4. **Đưa ngay đến cơ sở y tế gần nhất** để được can thiệp cấp cứu kịp thời."
    )
    return {
        "reply": text,
        "is_emergency": True,
        "suggestions": [
            "📞 Gọi cấp cứu ngay",
            "🏥 Địa chỉ Bệnh viện",
            "🕒 Quy trình cấp cứu 24/7",
        ],
        "actions": [
            {
                "type": "call",
                "label": f"Gọi Cấp cứu: {hotline}",
                "value": hotline.split("/")[0].strip(),
            },
            {
                "type": "link",
                "label": "Chỉ đường đến Bệnh viện",
                "url": "https://maps.google.com/?q=Bệnh+viện+Lao+và+Bệnh+phổi+Bạc+Liêu",
            },
        ],
    }


# --------------------------------------------------------------------------
# DVKT (Medical Service & Price Lookup) Integration
# --------------------------------------------------------------------------
PRICE_PATTERNS = [
    r"\bgia\b",
    r"\bbang gia\b",
    r"\bchi phi\b",
    r"\bbao nhieu tien\b",
    r"\bton bao nhieu\b",
    r"\btien kham\b",
    r"\bphi kham\b",
    r"\bhet bao nhieu\b",
    r"\bbang phi\b",
    r"\bvien phi\b",
]


def check_price_query(user_message: str) -> bool:
    norm = remove_accents(user_message)
    # Check exact word boundaries for price intent
    for pat in PRICE_PATTERNS:
        if re.search(pat, norm):
            return True
    # If mentions diagnostic technical services WITH a question of cost
    has_tech = any(re.search(rf"\b{k}\b", norm) for k in ["xquang", "x-quang", "ct", "genexpert", "afb", "phe dung", "ho hap ky", "noi soi"])
    has_ask = any(re.search(rf"\b{k}\b", norm) for k in ["bao nhieu", "tien", "phi", "gia"])
    return has_tech and has_ask


def search_dvkt_prices(user_message: str) -> dict | None:
    norm = remove_accents(user_message)
    all_dvkt = list(Dvkt.objects.all())
    if not all_dvkt:
        return None

    is_xray = any(k in norm for k in ["xquang", "x quang", "x-quang", "chup phoi", "chup phim", "x ray"])
    is_ct = any(k in norm for k in ["ct", "cat lop", "clvt"])
    is_sputum = any(k in norm for k in ["dom", "afb", "nhuom", "cay dom", "genexpert", "xpert"])
    is_lung_fx = any(k in norm for k in ["ho hap ky", "phe dung ky", "chuc nang ho hap", "spirometry"])
    is_endoscopy = any(k in norm for k in ["noi soi", "phe quan"])
    is_exam = any(k in norm for k in ["kham benh", "tien kham", "phi kham", "kham bao nhieu", "kham"])

    scored_items = []

    for item in all_dvkt:
        t_norm = remove_accents(item.ten_dich_vu)
        
        # Exclude invasive inpatient ICU procedures from patient price inquiries
        if any(bad in t_norm for bad in ["hut dom", "mo mang phoi", "soc dien", "choc hut mu", "dan luu mang phoi", "ong dan luu", "co dinh", "thut thao", "khong chuan bi"]):
            continue

        score = 0.0

        if is_xray:
            if "x-quang" in t_norm or "xquang" in t_norm:
                score += 20.0
                # Prioritize chest and lung X-rays for lung hospital
                has_other_body_part = any(b in norm for b in ["tay", "chan", "cot song", "khop", "bung", "so", "ham", "mat"])
                if not has_other_body_part:
                    if any(x in t_norm for x in ["nguc thang", "nguc nghieng", "dinh phoi", "tai giuong"]):
                        score += 30.0
                else:
                    # Match specific body parts requested
                    for b in ["tay", "chan", "cot song", "khop", "bung", "so"]:
                        if b in norm and b in t_norm:
                            score += 25.0

        elif is_ct:
            if "cat lop" in t_norm or "clvt" in t_norm or "ct" in t_norm:
                score += 20.0
                if any(x in t_norm for x in ["long nguc", "phoi"]):
                    score += 30.0
                elif any(b in t_norm for b in norm.split() if len(b) > 2):
                    score += 15.0

        elif is_sputum:
            if "afb" in t_norm:
                score += 35.0
            elif any(k in t_norm for k in ["xet nghiem", "cay", "nhuom", "dom"]):
                score += 15.0

        elif is_lung_fx:
            if any(k in t_norm for k in ["ho hap", "phe dung", "chuc nang"]):
                score += 30.0

        elif is_endoscopy:
            if "noi soi" in t_norm or "phe quan" in t_norm:
                score += 30.0

        elif is_exam:
            if "kham" in t_norm:
                score += 25.0
                if "lao" in t_norm or "noi" in t_norm:
                    score += 10.0

        # General token overlap boost
        q_tokens = tokenize(user_message)
        t_tokens = tokenize(item.ten_dich_vu)
        overlap = len(q_tokens.intersection(t_tokens))
        score += overlap * 5.0

        if score > 0:
            scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Take unique top items
    seen_codes = set()
    top_items = []
    for score, item in scored_items:
        if item.ma_dich_vu not in seen_codes:
            seen_codes.add(item.ma_dich_vu)
            top_items.append(item)
        if len(top_items) >= 6:
            break

    if not top_items:
        return None

    # Title header based on query
    header = "💰 **BẢNG GIÁ DỊCH VỤ KỸ THUẬT & XÉT NGHIỆM TẠI BỆNH VIỆN**\n"
    if is_xray:
        header = "📸 **BẢNG GIÁ CHỤP X-QUANG TẠI BỆNH VIỆN**\n"
    elif is_ct:
        header = "🖥️ **BẢNG GIÁ CHỤP CẮT LỚP VI TÍNH (CT SCANNER)**\n"
    elif is_sputum:
        header = "🔬 **BẢNG GIÁ XÉT NGHIỆM ĐỜM & PHÁT HIỆN LAO**\n"
    elif is_lung_fx:
        header = "📊 **BẢNG GIÁ ĐO CHỨC NĂNG HÔ HẤP (PHẾ DUNG KÝ)**\n"

    lines = [header]
    for item in top_items:
        gia = f"{int(item.don_gia):,} đ" if item.don_gia else "Theo quy định BYT"
        lines.append(f"• **{item.ten_dich_vu}** (Mã: `{item.ma_dich_vu}`): **{gia}**")

    if is_sputum or is_xray:
        lines.append(
            "\n💡 *Lưu ý đặc biệt:* Các xét nghiệm phát hiện Lao (AFB, GeneXpert) và thuốc điều trị Lao thuộc **Chương trình Chống lao Quốc gia được hỗ trợ miễn phí 100%**."
        )

    lines.append(
        "\n📌 *Chính sách BHYT:* Người bệnh có thẻ BHYT đúng tuyến hoặc diện chuyển tuyến được quỹ BHYT chi trả theo tỷ lệ quy định (80%, 95% hoặc 100%)."
    )
    lines.append("\n👉 Bạn có thể xem toàn bộ danh mục tại mục [Bảng giá Dịch vụ](/dich-vu.html).")

    return {
        "reply": "\n".join(lines),
        "is_emergency": False,
        "suggestions": [
            "💳 Quyền lợi BHYT chi trả như thế nào?",
            "🔬 Xét nghiệm phát hiện Lao có miễn phí không?",
            "📅 Đăng ký lịch khám trực tuyến",
        ],
        "actions": [
            {
                "type": "link",
                "label": "Tra cứu toàn bộ Bảng giá DVKT",
                "url": "./dich-vu.html",
            },
            {
                "type": "modal",
                "label": "Đặt lịch khám ngay",
                "action": "open_booking",
            },
        ],
    }


# --------------------------------------------------------------------------
# Booking / Appointment Intent Detection
# --------------------------------------------------------------------------
BOOKING_KEYWORDS = [
    r"\bdat lich\b",
    r"\bdang ky kham\b",
    r"\bhen gio\b",
    r"\bkham benh online\b",
    r"\blay so\b",
    r"\bdat cho\b",
]


def check_booking_intent(user_message: str) -> bool:
    norm = remove_accents(user_message)
    return any(re.search(pat, norm) for pat in BOOKING_KEYWORDS)


def get_booking_response() -> dict:
    text = (
        "📅 **ĐĂNG KÝ KHÁM BỆNH TRỰC TUYẾN**\n\n"
        "Bạn có thể đặt lịch hẹn khám trước tại Bệnh viện Lao và Bệnh phổi Bạc Liêu để được ưu tiên tiếp đón và giảm thời gian chờ đợi.\n\n"
        "**Các bước thực hiện:**\n"
        "1. Nhấn nút **Đặt lịch khám ngay** bên dưới.\n"
        "2. Điền Họ tên, Số điện thoại, Ngày khám mong muốn và Chuyên khoa / Triệu chứng.\n"
        "3. Hệ thống sẽ cấp cho bạn một **Mã đăng ký khám**.\n"
        "4. Nhân viên y tế sẽ liên hệ xác nhận và hướng dẫn bạn chu đáo."
    )
    return {
        "reply": text,
        "is_emergency": False,
        "suggestions": [
            "🕒 Bệnh viện khám những ngày nào?",
            "💳 Khám BHYT cần chuẩn bị giấy tờ gì?",
            "📞 Số điện thoại tư vấn bệnh viện",
        ],
        "actions": [
            {
                "type": "modal",
                "label": "Đặt lịch khám ngay",
                "action": "open_booking",
            }
        ],
    }


# --------------------------------------------------------------------------
# FAQ Knowledge Base Search & Scoring
# --------------------------------------------------------------------------
def search_faq_knowledge(user_message: str) -> tuple[ChatbotFAQ | None, list[str], float]:
    """Search knowledge base with multi-tier scoring."""
    faqs = list(ChatbotFAQ.objects.filter(is_active=True))
    if not faqs:
        return None, [], 0.0

    user_norm = remove_accents(user_message)
    user_tokens = tokenize(user_message)

    best_faq = None
    best_score = 0.0

    for faq in faqs:
        score = 0.0
        q_norm = remove_accents(faq.question)
        q_tokens = tokenize(faq.question)

        # 1. Exact or substring match in question
        if user_norm in q_norm or q_norm in user_norm:
            score += 30.0

        # 2. Token overlap with question
        overlap = len(user_tokens.intersection(q_tokens))
        if len(user_tokens) > 0:
            score += (overlap / len(user_tokens)) * 20.0

        # 3. Keyword tags match (word-level)
        if faq.keywords:
            raw_kws = [k.strip() for k in faq.keywords.split(",") if k.strip()]
            for kw in raw_kws:
                kw_norm = remove_accents(kw)
                if kw_norm:
                    if kw_norm in user_norm:
                        score += 15.0
                    elif set(kw_norm.split()).issubset(user_tokens):
                        score += 12.0

        # 4. Priority boost
        score += faq.priority * 0.5

        # 5. Intent / Category Affinity matching
        has_price = check_price_query(user_message)
        if has_price:
            if faq.category == ChatbotFAQCategory.DVKT_GIA:
                score += 25.0
            else:
                score -= 15.0
        else:
            if faq.category == ChatbotFAQCategory.DVKT_GIA:
                score -= 15.0

        if "bhyt" in user_norm or "bao hiem" in user_norm:
            if faq.category == ChatbotFAQCategory.BHYT:
                score += 25.0

        if any(w in user_norm for w in ["gio", "thoi gian", "khi nao", "mo cua", "lich lam"]):
            if faq.category == ChatbotFAQCategory.TIEP_DON:
                score += 20.0

        if score > best_score:
            best_score = score
            best_faq = faq

    # Match threshold
    if best_faq and best_score >= 5.0:
        ChatbotFAQ.objects.filter(id=best_faq.id).update(view_count=best_faq.view_count + 1)

        # Suggest related questions
        related = (
            ChatbotFAQ.objects.filter(is_active=True)
            .exclude(id=best_faq.id)
            .filter(category=best_faq.category)
            .values_list("question", flat=True)[:3]
        )
        if not related:
            related = (
                ChatbotFAQ.objects.filter(is_active=True)
                .exclude(id=best_faq.id)
                .values_list("question", flat=True)[:3]
            )
        return best_faq, list(related), best_score

    return None, [], best_score


# --------------------------------------------------------------------------
# Main Chat Engine
# --------------------------------------------------------------------------
def process_user_chat(user_message: str, session_id: str = "") -> dict:
    config = ChatbotConfig.get_solo()

    if not config.is_enabled:
        return {
            "success": False,
            "disabled": True,
            "reply": "Hệ thống Trợ lý ảo hiện đang tạm đóng để bảo trì. Quý khách vui lòng liên hệ hotline 0291 3 678 977.",
        }

    clean_msg = (user_message or "").strip()
    if not clean_msg:
        return {
            "success": True,
            "reply": config.welcome_message,
            "suggestions": config.quick_prompts_list[:4],
            "is_emergency": False,
        }

    # 1. Emergency Check (Highest priority!)
    if check_emergency(clean_msg):
        res = get_emergency_response(config)
        res["success"] = True
        return res

    # 2. Appointment Booking Intent
    if check_booking_intent(clean_msg):
        res = get_booking_response()
        res["success"] = True
        return res

    # 3. DVKT Technical Service & Price Query (when query has explicit price intent)
    if check_price_query(clean_msg):
        price_res = search_dvkt_prices(clean_msg)
        if price_res:
            price_res["success"] = True
            return price_res

    # 4. Check FAQ Knowledge Base (High priority for curated hospital guidance!)
    matched_faq, suggestions, faq_score = search_faq_knowledge(clean_msg)
    if matched_faq and faq_score >= 6.0:
        actions = []
        if matched_faq.category == ChatbotFAQCategory.BENH_LAO:
            actions.append(
                {
                    "type": "modal",
                    "label": "Đăng ký khám sàng lọc Lao",
                    "action": "open_booking",
                }
            )
        elif matched_faq.category == ChatbotFAQCategory.DVKT_GIA:
            actions.append(
                {
                    "type": "link",
                    "label": "Tra cứu toàn bộ Bảng giá DVKT",
                    "url": "./dich-vu.html",
                }
            )

        return {
            "success": True,
            "reply": matched_faq.answer,
            "matched_faq_id": matched_faq.id,
            "category": matched_faq.category,
            "suggestions": suggestions,
            "actions": actions,
            "is_emergency": False,
        }

    # 5. If medium FAQ score matched
    if matched_faq:
        actions = []
        if matched_faq.category == ChatbotFAQCategory.DVKT_GIA:
            actions.append(
                {
                    "type": "link",
                    "label": "Tra cứu bảng giá đầy đủ",
                    "url": "./dich-vu.html",
                }
            )
        return {
            "success": True,
            "reply": matched_faq.answer,
            "matched_faq_id": matched_faq.id,
            "category": matched_faq.category,
            "suggestions": suggestions,
            "actions": actions,
            "is_emergency": False,
        }

    # 6. Smart Fallback with suggestions
    fallback_suggestions = (
        list(
            ChatbotFAQ.objects.filter(is_active=True)
            .order_by("-priority", "-view_count")
            .values_list("question", flat=True)[:4]
        )
        or config.quick_prompts_list[:4]
    )

    return {
        "success": True,
        "reply": config.fallback_message,
        "suggestions": fallback_suggestions,
        "is_emergency": False,
        "actions": [
            {
                "type": "modal",
                "label": "Đặt lịch hẹn khám",
                "action": "open_booking",
            },
            {
                "type": "call",
                "label": f"Gọi tổng đài: {config.emergency_hotline}",
                "value": config.emergency_hotline.split("/")[0].strip(),
            },
        ],
    }
