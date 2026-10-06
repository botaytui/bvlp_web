from django.core.management.base import BaseCommand
from chatbot.models import ChatbotConfig, ChatbotFAQ, ChatbotFAQCategory


KNOWLEDGE_ITEMS = [
    # -------------------------------------------------------------------------
    # 1. ĐÓN TIẾP & GIỜ LÀM VIỆC
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.TIEP_DON,
        "question": "Thời gian làm việc và lịch khám bệnh của Bệnh viện như thế nào?",
        "answer": (
            "🕒 **THỜI GIAN LÀM VIỆC VÀ TIẾP ĐÓN:**\n\n"
            "• **Khám bệnh trong giờ hành chính:**\n"
            "  - Từ **Thứ Hai đến Thứ Sáu** hàng tuần.\n"
            "  - **Buổi sáng:** 07:00 – 11:30\n"
            "  - **Buổi chiều:** 13:00 – 16:30\n\n"
            "• **Khoa Cấp cứu & Điều trị Nội trú:** Phục vụ **24/24h** tất cả các ngày trong tuần, bao gồm cả Thứ Bảy, Chủ Nhật và các ngày Lễ, Tết.\n\n"
            "📞 Tổng đài tư vấn: **0291 3 678 977**"
        ),
        "keywords": "gio lam viec, lich kham, may gio mo cua, thu 7 co kham khong, chu nhat, thoi gian, lam viec ngoai gio, cap cuu 24/7",
        "priority": 10,
    },
    {
        "category": ChatbotFAQCategory.TIEP_DON,
        "question": "Địa chỉ Bệnh viện Lao và Bệnh phổi Bạc Liêu ở đâu? Đường đi như thế nào?",
        "answer": (
            "🏥 **ĐỊA CHỈ & THÔNG TIN LIÊN HỆ:**\n\n"
            "• **Tên đơn vị:** Bệnh viện Lao và Bệnh phổi Bạc Liêu\n"
            "• **Địa chỉ:** Đường Nguyễn Thị Minh Khai, Phường 5, TP. Bạc Liêu, Tỉnh Bạc Liêu.\n"
            "• **Số điện thoại:** 0291 3 678 977\n"
            "• **Email tiếp nhận thông tin:** bvbppbl@gmail.com\n\n"
            "🗺️ Bạn có thể tra cứu vị trí bệnh viện trên Google Maps hoặc nhấn vào mục **Liên hệ** trên menu để xem bản đồ chi tiết."
        ),
        "keywords": "dia chi o dau, duong di, benh vien o dau, so dien thoai, hotline, lien he, google maps",
        "priority": 9,
    },
    {
        "category": ChatbotFAQCategory.TIEP_DON,
        "question": "Tôi muốn đăng ký đặt lịch khám trước qua mạng có được không?",
        "answer": (
            "📅 **ĐĂNG KÝ KHÁM TRỰC TUYẾN TIỆN LỢI:**\n\n"
            "Hoàn toàn được! Bạn có thể đặt hẹn khám trước ngay trên website để tiết kiệm thời gian chờ đợi:\n\n"
            "1. Nhấn nút **Đặt lịch khám** ở góc trên màn hình hoặc biểu tượng lịch hẹn.\n"
            "2. Nhập thông tin: Họ tên, Số điện thoại, Ngày khám mong muốn và Lý do/Triệu chứng.\n"
            "3. Hệ thống sẽ cấp cho bạn một **Mã đăng ký khám**.\n"
            "4. Khi đến viện vào ngày đã hẹn, bạn chỉ cần xuất trình mã số tại quầy tiếp đón ưu tiên để vào thẳng phòng khám."
        ),
        "keywords": "dat lich, dang ky kham, lay so hen gio, dat cho, dang ky online, kham truoc",
        "priority": 8,
    },
    {
        "category": ChatbotFAQCategory.TIEP_DON,
        "question": "Quy trình các bước khám bệnh tại Bệnh viện diễn ra như thế nào?",
        "answer": (
            "📋 **QUY TRÌNH KHÁM BỆNH GỒM 5 BƯỚC:**\n\n"
            "1. **Bước 1 - Tiếp đón & Đăng ký:** Lấy số thứ tự, xuất trình CCCD/VNeID/Thẻ BHYT tại Quầy tiếp đón.\n"
            "2. **Bước 2 - Khám lâm sàng:** Bác sĩ chuyên khoa hô hấp thăm khám, khai thác tiền sử và chỉ định xét nghiệm cận lâm sàng cần thiết (nếu có).\n"
            "3. **Bước 3 - Thực hiện Cận lâm sàng:** Chụp X-quang tim phổi, đo phế dung ký, lấy mẫu đờm xét nghiệm vi khuẩn lao (GeneXpert/AFB), xét nghiệm máu.\n"
            "4. **Bước 4 - Bác sĩ kết luận:** Quay lại phòng khám ban đầu để bác sĩ đọc kết quả, chẩn đoán xác định và tư vấn phác đồ điều trị.\n"
            "5. **Bước 5 - Thanh toán & Lĩnh thuốc:** Thanh toán viện phí chênh lệch (nếu có) và nhận thuốc tại Khoa Dược BHYT hoặc nhận thuốc chương trình Chống lao miễn phí."
        ),
        "keywords": "quy trinh kham, cac buoc kham, huong dan kham benh, tiep don, lay so",
        "priority": 7,
    },

    # -------------------------------------------------------------------------
    # 2. BẢO HIỂM Y TẾ & THỦ TỤC CHUYỂN TUYẾN
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.BHYT,
        "question": "Đi khám BHYT cần mang theo những giấy tờ gì?",
        "answer": (
            "💳 **GIẤY TỜ CẦN CHUẨN BỊ KHI KHÁM BHYT:**\n\n"
            "Quý người bệnh vui lòng mang theo một trong các phương án sau:\n\n"
            "• **Phương án 1 (Tiện lợi nhất):** **Căn cước công dân gắn chip** đã tích hợp thông tin BHYT hoặc ứng dụng **VNeID mức 2** / **VssID** trên điện thoại thông minh.\n"
            "• **Phương án 2 (Truyền thống):** Thẻ BHYT giấy còn hạn sử dụng kèm theo Giấy tờ tùy thân có ảnh (CMND/CCCD/Bằng lái xe...).\n"
            "• **Giấy chuyển tuyến (nếu có):** Giấy chuyển viện từ cơ sở y tế tuyến dưới chuyển lên Bệnh viện Lao và Bệnh phổi Bạc Liêu.\n"
            "• **Sổ y bạ / Đơn thuốc cũ:** Mang theo các kết quả khám, phim X-quang hoặc đơn thuốc đang sử dụng (nếu có)."
        ),
        "keywords": "giay to bhyt, can mang gi, the bao hiem y te, can cuoc cong dan, cccd, vneid, vssid, giay chuyen vien, ho so",
        "priority": 10,
    },
    {
        "category": ChatbotFAQCategory.BHYT,
        "question": "Khám trái tuyến, không có giấy chuyển viện có được hưởng BHYT không?",
        "answer": (
            "📄 **QUY ĐỊNH HƯỞNG BHYT TRÁI TUYẾN / THÔNG TUYẾN:**\n\n"
            "Theo Luật Bảo hiểm Y tế hiện hành:\n\n"
            "1. **Trường hợp CẤP CỨU:** Người bệnh được tiếp nhận cấp cứu tại bất kỳ cơ sở y tế nào và được hưởng **100% quyền lợi BHYT** theo mức hưởng ghi trên thẻ, không cần giấy chuyển tuyến.\n"
            "2. **Điều trị NỘI TRÚ (Nằm viện):** Người bệnh có thẻ BHYT tự đến khám và có chỉ định nhập viện điều trị nội trú tại Bệnh viện Lao và Bệnh phổi Bạc Liêu (tuyến tỉnh) được quỹ BHYT thanh toán **100% chi phí điều trị nội trú** trong phạm vi mức hưởng.\n"
            "3. **Khám NGOẠI TRÚ (Khám xong về trong ngày):** Để được hưởng đầy đủ quyền lợi BHYT ngoại trú, người bệnh cần có Giấy chuyển tuyến hợp lệ từ cơ sở KCB ban đầu (Trạm y tế, Trung tâm y tế huyện/thị xã).\n\n"
            "💡 *Đặc biệt:* Thuốc điều trị Lao và các xét nghiệm phát hiện Lao thuộc Chương trình Chống lao Quốc gia được hỗ trợ **hoàn toàn miễn phí** không phân biệt tuyến!"
        ),
        "keywords": "trai tuyen, vuot tuyen, khong co giay chuyen vien, thong tuyen tinh, quyen loi bhyt, muc huong, nam vien",
        "priority": 9,
    },
    {
        "category": ChatbotFAQCategory.BHYT,
        "question": "Giấy chuyển tuyến BHYT có giá trị sử dụng trong bao lâu?",
        "answer": (
            "⏳ **THỜI HẠN HIỆU LỰC CỦA GIẤY CHUYỂN TUYẾN BHYT:**\n\n"
            "• **Khám chữa bệnh thông thường:** Giấy chuyển tuyến có giá trị sử dụng trong vòng **10 ngày làm việc** kể từ ngày ký phát hành để làm thủ tục tiếp nhận.\n"
            "• **Các bệnh mạn tính / Bệnh cần điều trị dài ngày (như Lao, Hen phế quản, COPD):** Giấy chuyển tuyến có giá trị sử dụng đến hết ngày **31 tháng 12 của năm dương lịch** cấp giấy.\n"
            "• **Tái khám theo hẹn:** Giấy hẹn khám lại chỉ có giá trị sử dụng **01 lần** trong thời hạn ghi trên giấy hẹn (thường không quá 30 ngày)."
        ),
        "keywords": "thoi han giay chuyen tuyen, giay chuyen vien dung duoc bao lau, giay hen tai kham, het nam duong lich",
        "priority": 6,
    },

    # -------------------------------------------------------------------------
    # 3. CHƯƠNG TRÌNH CHỐNG LAO & BỆNH LAO PHỔI
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.BENH_LAO,
        "question": "Những triệu chứng cảnh báo nào cho thấy cần đi khám Lao phổi ngay?",
        "answer": (
            "🩺 **CÁC DẤU HIỆU NGHI NGỜ MẮC LAO PHỔI:**\n\n"
            "Bạn cần đến Bệnh viện Lao và Bệnh phổi Bạc Liêu để khám sàng lọc ngay khi có các triệu chứng sau:\n\n"
            "1. ⚠️ **Ho dai dẳng kéo dài trên 2 tuần** (ho khan, ho có đờm hoặc ho ra máu).\n"
            "2. 🌡️ **Sốt nhẹ về chiều hoặc tối**, người ớn lạnh, gai sốt.\n"
            "3. 💦 **Đổ mồ hôi trộm ban đêm** (ướt áo gối dù trời mát).\n"
            "4. ⚖️ **Sụt cân không rõ nguyên nhân**, người mệt mỏi, chán ăn, suy nhược.\n"
            "5. 💔 **Đau tức ngực**, khó thở, thở dốc khi gắng sức.\n"
            "6. 👥 **Có tiền sử tiếp xúc gần** với người đang điều trị bệnh lao phổi."
        ),
        "keywords": "trieu chung lao, dau hieu benh lao, ho keo dai, sot ve chieu, do mo hoi dem, sut can, ho ra mau, lao phoi",
        "priority": 10,
    },
    {
        "category": ChatbotFAQCategory.BENH_LAO,
        "question": "Bệnh Lao có chữa khỏi hoàn toàn được không? Mất bao lâu?",
        "answer": (
            "✅ **BỆNH LAO HOÀN TOÀN CÓ THỂ CHỮA KHỎI 100%!**\n\n"
            "Y học hiện đại khẳng định bệnh lao hoàn toàn có thể chữa khỏi dứt điểm nếu người bệnh tuân thủ đúng nguyên tắc **DOTS (Điều trị có kiểm soát trực tiếp)**:\n\n"
            "• **Thời gian điều trị:** Phác đồ lao nhạy cảm thường kéo dài từ **6 đến 8 tháng** (chia thành 2 giai đoạn: Giai đoạn tấn công 2 tháng và Giai đoạn duy trì 4-6 tháng).\n"
            "• **Nguyên tắc 3 ĐÚNG:**\n"
            "  1. **Đúng thuốc & đúng liều:** Uống đủ các loại thuốc phối hợp do bác sĩ chỉ định theo cân nặng.\n"
            "  2. **Đều đặn:** Uống thuốc hàng ngày vào một giờ cố định (thường vào buổi sáng trước khi ăn 30 phút).\n"
            "  3. **Đủ thời gian:** Tuyệt đối không tự ý bỏ thuốc, giảm liều ngay cả khi cảm thấy người đã khỏe mạnh bình thường."
        ),
        "keywords": "benh lao chua khoi khong, thoi gian uong thuoc, bao lau thi khoi, phac do dieu tri lao, uong thuoc may thang",
        "priority": 9,
    },
    {
        "category": ChatbotFAQCategory.BENH_LAO,
        "question": "Thuốc điều trị bệnh Lao và xét nghiệm phát hiện Lao có mất tiền không?",
        "answer": (
            "🎁 **CHÍNH SÁCH HỖ TRỢ MIỄN PHÍ CỦA CHƯƠNG TRÌNH CHỐNG LAO QUỐC GIA:**\n\n"
            "• **Thuốc chống lao:** Toàn bộ thuốc điều trị Lao phác đồ chuẩn hàng 1 được Chương trình Chống lao Quốc gia (CTCLQG) và Quỹ BHYT **CẤP PHÁT HOÀN TOÀN MIỄN PHÍ** cho người bệnh trong suốt liệu trình điều trị.\n"
            "• **Xét nghiệm chẩn đoán:** Các xét nghiệm sàng lọc then chốt như Soi đờm trực tiếp (AFB) và Kỹ thuật sinh học phân tử GeneXpert được hỗ trợ theo quy định của dự án và quỹ BHYT.\n\n"
            "➡️ Đừng vì lo lắng chi phí mà trì hoãn khám bệnh. Hãy đến Bệnh viện để được bác sĩ khám và bảo vệ sức khỏe cho chính bạn và gia đình!"
        ),
        "keywords": "thuoc lao co mat tien khong, thuoc mien phi, chuong trinh chong lao quoc gia, chi phi dieu tri lao, tro cap",
        "priority": 9,
    },
    {
        "category": ChatbotFAQCategory.BENH_LAO,
        "question": "Lao tiềm ẩn là gì? Ai cần tầm soát và điều trị dự phòng lao?",
        "answer": (
            "🛡️ **LAO TIỀM ẨN (LTBI) VÀ ĐIỀU TRỊ DỰ PHÒNG:**\n\n"
            "• **Lao tiềm ẩn là gì?** Là tình trạng cơ thể đã nhiễm vi khuẩn lao (Mycobacterium tuberculosis) nhưng vi khuẩn đang 'ngủ yên', chưa gây tổn thương phổi, không có triệu chứng và **KHÔNG lây cho người khác**.\n"
            "• **Tại sao cần điều trị?** Khoảng 5-10% người nhiễm lao tiềm ẩn sẽ phát triển thành bệnh lao hoạt tính trong đời khi sức đề kháng suy giảm.\n"
            "• **Đối tượng cần tầm soát & điều trị dự phòng:**\n"
            "  - Người tiếp xúc hộ gia đình (sống chung nhà) với bệnh nhân lao phổi.\n"
            "  - Trẻ em dưới 5 tuổi tiếp xúc nguồn lây.\n"
            "  - Người có bệnh lý nền suy giảm miễn dịch (HIV, đái tháo đường, suy thận mạn, đang dùng thuốc ức chế miễn dịch).\n"
            "• **Xét nghiệm phát hiện:** Test da Mantoux (TST) hoặc xét nghiệm máu IGRA (QuantiFERON-TB)."
        ),
        "keywords": "lao tiem an, ltbi, du phong lao, tiep xuc voi nguoi bi lao, quantiferon, mantoux, xet nghiem mau",
        "priority": 7,
    },
    {
        "category": ChatbotFAQCategory.BENH_LAO,
        "question": "Làm thế nào để phòng tránh lây nhiễm vi khuẩn Lao cho người thân trong gia đình?",
        "answer": (
            "🏡 **HƯỚNG DẪN PHÒNG LÂY NHIỄM LAO TẠI GIA ĐÌNH:**\n\n"
            "1. **Đeo khẩu trang y tế:** Người bệnh cần đeo khẩu trang liên tục trong 2 - 4 tuần đầu điều trị khi tiếp xúc với người xung quanh.\n"
            "2. **Che miệng khi ho, hắt hơi:** Dùng khăn giấy che miệng khi ho, khạc đờm vào cốc giấy có nắp đậy và bỏ đúng nơi quy định, không khạc nhổ bừa bãi.\n"
            "3. **Thông gió nơi ở:** Phòng ở của người bệnh cần mở cửa sổ thông thoáng, đón ánh nắng mặt trời tự nhiên (tia cực tím trong ánh nắng diệt vi khuẩn lao rất nhanh).\n"
            "4. **Vệ sinh tay:** Thường xuyên rửa tay bằng xà phòng hoặc dung dịch sát khuẩn.\n"
            "5. **Khám sàng lọc cho người nhà:** Đưa tất cả thành viên sống chung nhà đến Bệnh viện Lao và Bệnh phổi Bạc Liêu để chụp X-quang và xét nghiệm tầm soát."
        ),
        "keywords": "phong ngua lay nhiem, lay qua duong nao, cham soc nguoi bi lao, cach ly, nguoi nha bi lao, deo khau trang",
        "priority": 7,
    },

    # -------------------------------------------------------------------------
    # 4. BỆNH PHỔI - HÔ HẤP (HEN PHẾ QUẢN, COPD, VIÊM PHỔI)
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.HO_HAP,
        "question": "Bệnh Hen phế quản (Suyễn) có biểu hiện gì? Khám và điều trị ra sao?",
        "answer": (
            "🩺 **TƯ VẤN HEN PHẾ QUẢN (HEN SUYỄN):**\n\n"
            "• **Triệu chứng điển hình:** Khó thở từng cơn, thở khò khè hoặc rít lên như tiếng huýt sáo, nặng ngực, ho nhiều về đêm hoặc sáng sớm, cơn khó thở tăng lên khi thay đổi thời tiết, tiếp xúc khói bụi, lông thú nuôi.\n"
            "• **Chẩn đoán tại Bệnh viện:** Khám chuyên khoa hô hấp kết hợp **Đo chức năng hô hấp (Phế dung ký)** có làm test hồi phục phế quản.\n"
            "• **Điều trị:** Bệnh viện có Phòng quản lý Hen ngoại trú cấp thuốc kiểm soát dạng xịt/hít (ICS-LABA) theo BHYT giúp người bệnh sinh hoạt hoàn toàn bình thường, ngăn ngừa cơn hen cấp tính nguy hiểm."
        ),
        "keywords": "hen phe quan, hen suyen, kho khe, tho rit, kho tho ve dem, thuoc xit hen, phong quan ly hen, ho hap ky",
        "priority": 8,
    },
    {
        "category": ChatbotFAQCategory.HO_HAP,
        "question": "Bệnh phổi tắc nghẽn mạn tính (COPD) là gì? Ai hay mắc phải?",
        "answer": (
            "🚬 **BỆNH PHỔI TẮC NGHẼN MẠN TÍNH (COPD):**\n\n"
            "• **COPD là gì?** Là tình trạng tắc nghẽn luồng khí thở mạn tính không hồi phục hoàn toàn, thường tiến triển nặng dần theo thời gian.\n"
            "• **Đối tượng nguy cơ cao:**\n"
            "  - Người có tiền sử hút thuốc lá, thuốc lào nhiều năm (kể cả hút thuốc thụ động).\n"
            "  - Người thường xuyên tiếp xúc khói bếp than, khói củi, bụi công nghiệp, hóa chất.\n"
            "• **Dấu hiệu nhận biết:** Ho khạc đờm mạn tính vào mỗi buổi sáng, khó thở tăng dần khi đi bộ hoặc leo cầu thang, cảm giác hụt hơi.\n"
            "• **Điều trị:** Đo chức năng thông khí phổi định kỳ, cai thuốc lá tuyệt đối và sử dụng thuốc giãn phế quản duy trì theo phác đồ bác sĩ."
        ),
        "keywords": "copd, phoi tac nghen man tinh, hut thuoc la, hut thuoc lao, ho khac dom buoi sang, hut hoi, kho tho khi gang suc",
        "priority": 8,
    },
    {
        "category": ChatbotFAQCategory.HO_HAP,
        "question": "Đo chức năng hô hấp (Hô hấp ký / Phế dung ký) là gì? Cần chuẩn bị gì trước khi đo?",
        "answer": (
            "📊 **ĐO CHỨC NĂNG THÔNG KHÍ PHỔI (SPIROMETRY):**\n\n"
            "• **Mục đích:** Đánh giá dung tích phổi và mức độ thông thoáng của đường thở, là tiêu chuẩn vàng để chẩn đoán Hen phế quản và COPD.\n"
            "• **Lưu ý chuẩn bị trước khi đo:**\n"
            "  - Mặc quần áo rộng rãi, thoải mái, không nịt chặt ngực bụng.\n"
            "  - Không hút thuốc lá ít nhất 1 giờ trước khi đo.\n"
            "  - Không uống rượu bia ít nhất 4 giờ trước khi đo.\n"
            "  - Không ăn quá no trong vòng 2 giờ trước khi đo.\n"
            "  - Báo với nhân viên y tế các loại thuốc xịt/hít giãn phế quản đã dùng gần nhất."
        ),
        "keywords": "do chuc nang ho hap, ho hap ky, phe dung ky, spirometry, do phoi, do dung tich phoi, luu y truoc khi do",
        "priority": 7,
    },

    # -------------------------------------------------------------------------
    # 5. BẢNG GIÁ DỊCH VỤ & XÉT NGHIỆM KỸ THUẬT
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.DVKT_GIA,
        "question": "Bảng giá một số dịch vụ kỹ thuật và xét nghiệm chính tại Bệnh viện?",
        "answer": (
            "💰 **BẢNG GIÁ THAM KHẢO CÁC DỊCH VỤ CHÍNH TẠI BỆNH VIỆN:**\n\n"
            "• **Khám bệnh chuyên khoa:** ~38.700 đ / lượt\n"
            "• **Chụp X-quang ngực thẳng (Kỹ thuật số):** ~65.000 – 72.000 đ / lần\n"
            "• **Chụp Cắt lớp vi tính (CT Scanner) lồng ngực:** ~519.000 – 1.050.000 đ (tùy có thuốc cản quang hay không)\n"
            "• **Đo chức năng hô hấp (Phế dung ký):** ~120.000 – 160.000 đ\n"
            "• **Xét nghiệm GeneXpert phát hiện Lao/Kháng thuốc:** Theo danh mục BHYT / Chương trình Chống lao hỗ trợ\n"
            "• **Nội soi phế quản ống mềm:** ~700.000 – 950.000 đ\n\n"
            "📌 *Lưu ý:* Giá trên áp dụng theo khung giá DVKT được Sở Y tế phê duyệt. Người bệnh có thẻ BHYT sẽ được quỹ BHYT chi trả theo tỷ lệ quy định (80%, 95% hoặc 100%).\n"
            "👉 Xem chi tiết tại mục **[Bảng giá Dịch vụ](/dich-vu.html)**."
        ),
        "keywords": "gia xet nghiem, gia chup xquang, chup ct bao nhieu tien, chi phi kham, bang gia vien phi, gia do ho hap",
        "priority": 10,
    },
    {
        "category": ChatbotFAQCategory.DVKT_GIA,
        "question": "Xét nghiệm GeneXpert là gì? Thời gian trả kết quả bao lâu?",
        "answer": (
            "🔬 **KỸ THUẬT XÉT NGHIỆM GENEXPERT (PCR ĐỘT PHÁ):**\n\n"
            "• **GeneXpert MTB/RIF là gì?** Là kỹ thuật sinh học phân tử tự động hiện đại bậc nhất hiện nay, cho phép phát hiện trực tiếp ADN của vi khuẩn lao và phát hiện đột biến kháng thuốc Rifampicin.\n"
            "• **Ưu điểm vượt trội:**\n"
            "  - Độ nhạy và độ đặc hiệu cực cao (> 98%).\n"
            "  - Cho kết quả nhanh chóng chỉ sau **2 giờ** (so với phương pháp nuôi cấy truyền thống mất từ 4 - 8 tuần).\n"
            "• **Mẫu bệnh phẩm:** Bệnh nhân chỉ cần lấy mẫu đờm buổi sáng theo hướng dẫn của kỹ thuật viên."
        ),
        "keywords": "genexpert, xet nghiem gene xpert, xpert mtb rif, xet nghiem pcr lao, bao lau co ket qua, khang thuoc rifampicin",
        "priority": 8,
    },

    # -------------------------------------------------------------------------
    # 6. CẤP CỨU & DẤU HIỆU NGUY HIỂM
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.CAP_CUU,
        "question": "Cần làm gì khi người bệnh bị ho ra máu?",
        "answer": (
            "🚨 **HƯỚNG DẪN XỬ TRÍ CẤP CỨU HO RA MÁU:**\n\n"
            "Ho ra máu là tình trạng cấp cứu nguy hiểm, có thể đe dọa tính mạng do tắc nghẽn đường thở:\n\n"
            "1. **Bình tĩnh & Đặt tư thế an toàn:** Cho người bệnh nằm nghỉ tuyệt đối ở tư thế đầu cao hoặc nằm nghiêng về bên nghi ngờ tổn thương (để tránh máu tràn sang phổi lành).\n"
            "2. **Đảm bảo thông thoáng đường thở:** Động viên người bệnh ho nhẹ nhàng để tống máu đông ra ngoài, **tuyệt đối không nuốt máu**.\n"
            "3. **Không tự ý uống thuốc:** Không tự ý cho uống nước nóng, không dùng thuốc dân gian khi chưa có chỉ định y khoa.\n"
            "4. **Gọi cấp cứu ngay lập tức:** Gọi **115** hoặc Hotline Bệnh viện: **0291 3 678 977** để được xe cấp cứu hỗ trợ chuyển viện an toàn."
        ),
        "keywords": "ho ra mau, khac ra mau, so cuu ho ra mau, chay mau phoi, cap cuu ho hap, nghet tho, mau dong",
        "priority": 10,
    },
    {
        "category": ChatbotFAQCategory.CAP_CUU,
        "question": "Khi nào người bệnh cần đi cấp cứu ngay lập tức?",
        "answer": (
            "🚑 **CÁC DẤU HIỆU HÔ HẤP NGUY HIỂM CẦN ĐI CẤP CỨU NGAY:**\n\n"
            "Hãy đưa người bệnh đến Khoa Cấp cứu BV Lao & Bệnh Phổi Bạc Liêu ngay nếu xuất hiện bất kỳ dấu hiệu nào sau đây:\n\n"
            "• Khó thở dữ dội, tím tái môi và đầu ngón tay chân.\n"
            "• Ho khạc ra máu tươi số lượng nhiều hoặc ho ra máu liên tục không cầm.\n"
            "• Đau ngực đột ngột, dữ dội, kèm theo vã mồ hôi lạnh, tụt huyết áp.\n"
            "• Thở rít, co kéo cơ hô hấp ở cổ và lồng ngực (cơn hen ác tính).\n"
            "• Lơ mơ, lẫn lộn, hôn mê do thiếu oxy não.\n\n"
            "🏥 Khoa Cấp cứu Bệnh viện trực 24/24h - Hotline: **0291 3 678 977**."
        ),
        "keywords": "khi nao can cap cuu, dau hieu cap cuu, kho tho du doi, tim tai, ngat tho, dau nguc cap, goi 115",
        "priority": 10,
    },

    # -------------------------------------------------------------------------
    # 7. TIỆN ÍCH & THÔNG TIN KHÁC
    # -------------------------------------------------------------------------
    {
        "category": ChatbotFAQCategory.TIEN_ICH,
        "question": "Bệnh viện có các khoa phòng chuyên môn nào?",
        "answer": (
            "🏥 **CÁC KHOA PHÒNG CHUYÊN MÔN TẠI BỆNH VIỆN:**\n\n"
            "• **Khối Lâm sàng:**\n"
            "  - Khoa Khám bệnh - Cấp cứu\n"
            "  - Khoa Lao & Bệnh phổi người lớn (Nội Lao)\n"
            "  - Khoa Hô hấp & Bệnh phổi mạn tính (Hen - COPD)\n"
            "  - Khoa Hồi sức tích cực - Chống độc\n"
            "  - Khoa Kiểm soát nhiễm khuẩn\n"
            "• **Khối Cận lâm sàng & Dược:**\n"
            "  - Khoa Chẩn đoán hình ảnh (X-quang, CT-Scanner)\n"
            "  - Khoa Xét nghiệm (Vi sinh - GeneXpert, Huyết học, Sinh hóa)\n"
            "  - Khoa Dược - Vật tư y tế\n"
            "• **Phòng chức năng:** Kế hoạch tổng hợp, Điều dưỡng, Tổ chức cán bộ, Tài chính kế toán."
        ),
        "keywords": "khoa phong, cac khoa chuyen mon, khoa kham benh, khoa hoi suc, khoa xet nghiem, khoa duoc",
        "priority": 5,
    },
    {
        "category": ChatbotFAQCategory.TIEN_ICH,
        "question": "Chế độ dinh dưỡng và chăm sóc cho người bệnh phổi như thế nào?",
        "answer": (
            "🥗 **LỜI KHUYÊN DINH DƯỠNG & CHĂM SÓC NGƯỜI BỆNH PHỔI:**\n\n"
            "• **Chế độ ăn giàu đạm (Protein):** Bổ sung thịt nạc, cá, trứng, sữa, đậu hũ để tái tạo mô tổn thương và tăng sức đề kháng.\n"
            "• **Bổ sung Vitamin & Khoáng chất:** Ăn nhiều rau xanh, trái cây tươi giàu Vitamin C, Vitamin A, Kẽm (cam, bưởi, ổi, cà rốt, súp lơ...).\n"
            "• **Uống đủ nước:** Uống 1.5 - 2 lít nước ấm mỗi ngày giúp làm loãng đờm nhớt, dễ tống xuất khi ho.\n"
            "• **Kiêng cữ:** Tránh xa thuốc lá, rượu bia, đồ uống có cồn, hạn chế đồ chiên xào nhiều dầu mỡ và thức ăn cay nóng gây kích ứng họng.\n"
            "• **Tập thở:** Thực hiện bài tập thở chúm môi và thở cơ hoành mỗi ngày theo hướng dẫn của điều dưỡng."
        ),
        "keywords": "dinh duong cho nguoi bi lao, an gi khi bi ho, cham soc benh nhan phoi, tap tho chum moi, kieng an gi",
        "priority": 5,
    },
]


class Command(BaseCommand):
    help = "Khoi tao du lieu tri thuc y te va FAQ cho Chatbot"

    def handle(self, *args, **options):
        self.stdout.write("Khoi tao cau hinh va du lieu tri thuc Chatbot...")

        # 1. Init ChatbotConfig singleton
        config, created = ChatbotConfig.objects.get_or_create(
            id=1,
            defaults={
                "is_enabled": True,
                "bot_name": "Trợ lý Y tế BV Lao & Bệnh Phổi Bạc Liêu",
                "welcome_message": (
                    "Xin chào! Tôi là **Trợ lý AI Bệnh viện Lao và Bệnh phổi Bạc Liêu** ✨.\n\n"
                    "Tôi có thể hỗ trợ bạn:\n"
                    "• Tra cứu lịch làm việc & quy trình khám BHYT\n"
                    "• Sàng lọc triệu chứng nghi ngờ bệnh Lao & Bệnh Hô hấp\n"
                    "• Tra cứu bảng giá xét nghiệm, X-quang, CT Scan\n"
                    "• Đăng ký khám trực tuyến và hướng dẫn cấp cứu\n\n"
                    "Bạn cần hỗ trợ thông tin gì hôm nay?"
                ),
                "emergency_hotline": "0291 3 678 977",
                "disclaimer_text": (
                    "Lưu ý: Thông tin tư vấn chỉ mang tính tham khảo y tế, không thay thế việc khám và chẩn đoán trực tiếp từ Bác sĩ."
                ),
            },
        )
        if created:
            self.stdout.write("Da tao ChatbotConfig mac dinh.")
        else:
            self.stdout.write("ChatbotConfig da ton tai.")

        # 2. Seed FAQ items
        imported_count = 0
        updated_count = 0
        for item in KNOWLEDGE_ITEMS:
            faq, was_created = ChatbotFAQ.objects.update_or_create(
                question=item["question"],
                defaults={
                    "category": item["category"],
                    "answer": item["answer"],
                    "keywords": item["keywords"],
                    "priority": item.get("priority", 0),
                    "is_active": True,
                },
            )
            if was_created:
                imported_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            f"Hoan thanh! Da them moi: {imported_count}, Cap nhat: {updated_count} cau hoi FAQ."
        )
