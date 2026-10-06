import json
import re
import threading
import time
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path

PHONE = '0291 3 678 977'
OA = 'https://zalo.me/bvlaophoibaclieu'
BOOKING = 'https://bvlbpbl.vn/index.php/dat-lich-kham-benh.html'
PRICING = 'https://bvlbpbl.vn/index.php/gia-dich-vu/danh-muc-dich-vu-ky-thuat.html'
FAQ_PATH = Path(__file__).with_name('faq.json')
SUGGESTIONS = ['Đặt lịch khám', 'Giấy tờ BHYT', 'Giá X-quang ngực', 'Gặp nhân viên']


def normalize(text):
    text = unicodedata.normalize('NFD', text.lower()).replace('đ', 'd')
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', text).split())


def contains(text, phrase):
    return f' {normalize(phrase)} ' in f' {text} '


def load_faq():
    return json.loads(FAQ_PATH.read_text(encoding='utf-8'))


def result(text, topic, actions=None, faq=None):
    return {'reply': text, 'topic': topic, 'actions': actions or [],
            'suggestions': SUGGESTIONS, 'faq_id': faq['id'] if faq else None,
            'sources': faq['sources'] if faq else [],
            'review_status': faq['review_status'] if faq else 'pilot_guidance'}


def human():
    return result(f'Anh/chị nhắn OA bệnh viện hoặc gọi {PHONE} để được hỗ trợ. Đây là hướng dẫn liên hệ; chưa xác nhận nhân viên đã nhận yêu cầu.', 'handoff',
                  [{'label': 'Nhắn OA bệnh viện', 'url': OA}, {'label': 'Gọi bệnh viện', 'url': 'tel:02913678977'}])


class Engine:
    """Retrieval only. Keeps topics in RAM, never stores raw messages or patient records."""
    def __init__(self, price_provider=lambda: []):
        self.faqs = load_faq()
        self.price_provider = price_provider
        self.sessions = {}
        self.lock = threading.Lock()

    def answer(self, message, session='preview'):
        norm = normalize(message)
        with self.lock:
            now = time.monotonic()
            self.sessions = {k:v for k,v in self.sessions.items() if now-v[1] < 900}
            context = self.sessions.get(session, ('', 0))[0]
            # Bound session cardinality even when the preview receives many session IDs.
            if len(self.sessions) >= 500 and session not in self.sessions:
                self.sessions.pop(next(iter(self.sessions)))
        answer = self._answer(norm, context)
        with self.lock:
            self.sessions[session] = (answer['topic'], time.monotonic())
        return answer

    def _answer(self, norm, context):
        # Fixed routing precedes FAQ search; do not let booking/pricing hide urgent phrases.
        if any(contains(norm, p) for p in ['không thở được', 'khó thở dữ dội', 'bất tỉnh', 'đau ngực dữ dội', 'ho ra máu', 'cấp cứu']):
            return result('Nếu đang cần cấp cứu, gọi 115 hoặc đến cơ sở cấp cứu gần nhất; không chờ phản hồi qua chat. Bot không đánh giá tình trạng cấp cứu hay thay thế nhân viên y tế.', 'emergency', [{'label':'Gọi 115', 'url':'tel:115'}])
        if any(contains(norm, p) for p in ['nhân viên', 'người thật', 'tư vấn viên', 'gặp bác sĩ']):
            return human()
        if norm in ('', 'hi', 'hello', 'xin chao', 'chao', 'menu', 'bat dau', 'start'):
            return result('Xin chào! Đây là trợ lý hướng dẫn của Bệnh viện Lao và Bệnh phổi Bạc Liêu, bản thử nghiệm hướng dẫn thủ tục. Anh/chị muốn đặt lịch, xem hướng dẫn BHYT, tra giá dịch vụ hay liên hệ nhân viên?', 'welcome')
        if norm in ('cam on', 'thanks'):
            return result('Rất vui được hỗ trợ anh/chị. Anh/chị cần xem thêm hướng dẫn nào?', 'welcome')
        if context == 'booking' and any(contains(norm, p) for p in ['cần giấy tờ', 'mang gì', 'chuẩn bị gì']):
            norm = 'giay to bhyt'
        if context == 'bhyt' and norm in ('con trai tuyen', 'trai tuyen thi sao', 'trai tuyen', 'con chuyen tuyen'):
            norm = 'bhyt trai tuyen'
        if any(contains(norm, p) for p in ['giá', 'chi phí', 'bao nhiêu tiền', 'bảng giá', 'phí khám', 'khám bao nhiêu']):
            return self.prices(norm)
        clinical = ['uống thuốc', 'liều thuốc', 'kê đơn', 'chẩn đoán', 'có bị lao', 'ho kéo dài', 'đọc kết quả', 'kết quả của tôi', 'bệnh án']
        if any(contains(norm, p) for p in clinical):
            return result(f'Bot hướng dẫn thủ tục chưa truy xuất hồ sơ cá nhân, chẩn đoán hoặc kê thuốc. Anh/chị liên hệ nơi khám hoặc gọi {PHONE} để được nhân viên xác minh và bác sĩ hướng dẫn.', 'clinical', [{'label':'Liên hệ OA', 'url':OA}])
        ranked = []
        for faq in self.faqs:
            # Pilot answers are drafts derived from existing OA guidance; never pretend approved.
            score = 0
            for phrase in faq['aliases'] + [faq['question']]:
                p = normalize(phrase)
                if norm == p:
                    score = max(score, 100 + len(p))
                elif contains(norm, p):
                    score = max(score, 20 + len(p))
            if score:
                ranked.append((score, faq))
        if ranked:
            faq = max(ranked, key=lambda x:x[0])[1]
            return result(faq['answer'], faq['topic'], faq.get('actions'), faq)
        return result('Tôi chưa tìm được hướng dẫn phù hợp. Anh/chị có thể nói rõ muốn hỏi về đặt lịch, BHYT hay tên dịch vụ cần tra giá; hoặc nhắn OA bệnh viện để được hỗ trợ.', 'unknown', [{'label':'Nhắn OA', 'url':OA}])

    def prices(self, norm):
        query = norm
        for term in ['bang gia', 'bao nhieu tien', 'chi phi', 'bao nhieu', 'gia', 'phi', 'toi', 'muon', 'biet', 'la', 'va', 'co', 'khong', 'dich vu']:
            query = re.sub(r'\b' + re.escape(term) + r'\b', ' ', query)
        query = ' '.join(query.split()).replace('x quang', 'xquang')
        query = query.replace('kham benh', 'kham')
        query = re.sub(r'\bct\b', 'cat lop vi tinh', query)
        if 'xquang' in query or 'cat lop vi tinh' in query:
            query = re.sub(r'\bphoi\b', 'nguc', query)
        if not query:
            return result('Anh/chị muốn tra giá dịch vụ nào? Ví dụ: giá X-quang ngực, CT ngực hoặc khám bệnh.', 'pricing', [{'label':'Bảng giá bệnh viện', 'url':PRICING}])
        try:
            items = self.price_provider()
        except Exception:
            return result(f'Hiện chưa tải được bảng giá. Anh/chị xem bảng giá công bố hoặc gọi {PHONE} để xác nhận.', 'pricing', [{'label':'Bảng giá bệnh viện', 'url':PRICING}])
        words = set(query.split())
        matches = []
        for item in items:
            name = normalize(item.get('ten_dich_vu', '')).replace('x quang', 'xquang')
            code = normalize(item.get('ma_dich_vu', ''))
            # Chest and thoracic-spine X-rays share 'ngực'; do not mix these indications.
            if 'nguc' in query and 'cot song' not in query and 'cot song' in name:
                continue
            # Require all service terms; generic 'giá' must not retrieve unrelated procedures.
            if query == code or words.issubset(set(name.split())):
                matches.append(item)
        matches.sort(key=lambda i:len(i.get('ten_dich_vu', '')))
        lines = []
        for item in matches[:4]:
            try:
                price = Decimal(str(item.get('don_gia')))
                if not price.is_finite() or price < 0:
                    raise InvalidOperation()
                amount = f'{price:,.0f}'.replace(',', '.') + ' đ'
            except (InvalidOperation, TypeError, ValueError):
                amount = 'Chưa có đơn giá'
            lines.append(f"• {item['ten_dich_vu']} (mã {item.get('ma_dich_vu', '')}): {amount}")
        if not lines:
            text = 'Chưa tìm thấy dịch vụ khớp tên/mã anh/chị hỏi. Vui lòng nhập tên cụ thể hơn hoặc hỏi quầy tiếp nhận.'
        else:
            text = 'Giá tham khảo từ bảng giá đang phục vụ website bệnh viện:\n\n' + '\n'.join(lines)
            if len(matches) > 4:
                text += f'\nCòn {len(matches)-4} mục phù hợp; vui lòng nêu rõ kỹ thuật để thu hẹp kết quả.'
            text += '\n\nChi phí thực tế và quyền lợi BHYT cần được bệnh viện xác nhận. Đây không phải báo giá toàn bộ lần khám.'
        return result(text, 'pricing', [{'label':'Xem bảng giá công bố', 'url':PRICING}])
