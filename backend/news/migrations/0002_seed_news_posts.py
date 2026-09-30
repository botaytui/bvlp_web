import datetime

from django.db import migrations


POSTS = [
    {
        'title': 'Hướng dẫn đăng ký khám trực tuyến',
        'slug': 'huong-dan-dang-ky-kham-truc-tuyen',
        'category': 'announcement',
        'summary': 'Người bệnh có thể gửi thông tin trực tuyến để bệnh viện chủ động liên hệ xác nhận lịch khám.',
        'content': (
            'Người bệnh điền họ tên, số điện thoại và ngày khám mong muốn trên biểu mẫu đăng ký khám trực tuyến. '
            'Nếu chưa xác định được chuyên khoa, người bệnh có thể mô tả ngắn gọn triệu chứng để nhân viên bệnh viện hỗ trợ phân luồng.\n\n'
            'Sau khi gửi thành công, hệ thống cung cấp mã đăng ký. Nhân viên bệnh viện sẽ liên hệ qua số điện thoại đã cung cấp để xác nhận thời gian khám.\n\n'
            'Khi đến khám, người bệnh vui lòng mang theo giấy tờ tùy thân, thẻ bảo hiểm y tế và các kết quả khám trước đây nếu có.'
        ),
        'cover_image_url': './assets/images/news-3.png',
        'status': 'published',
        'is_featured': True,
        'published_at': datetime.datetime(2026, 9, 26, 1, 0, tzinfo=datetime.timezone.utc),
    },
    {
        'title': 'Tăng cường phát hiện sớm bệnh lao trong cộng đồng',
        'slug': 'tang-cuong-phat-hien-som-benh-lao-trong-cong-dong',
        'category': 'news',
        'summary': 'Chủ động tầm soát, điều trị kịp thời vì một cộng đồng khỏe mạnh hơn.',
        'content': (
            'Phát hiện sớm bệnh lao giúp người bệnh được điều trị kịp thời và giảm nguy cơ lây truyền trong cộng đồng. '
            'Người có triệu chứng ho kéo dài, sốt nhẹ về chiều, ra mồ hôi đêm hoặc sụt cân không rõ nguyên nhân nên đến cơ sở y tế để được tư vấn.\n\n'
            'Người bệnh cần tuân thủ hướng dẫn và dùng thuốc đầy đủ theo phác đồ của nhân viên y tế.'
        ),
        'cover_image_url': './assets/images/news-1.png',
        'status': 'published',
        'is_featured': False,
        'published_at': datetime.datetime(2024, 4, 12, 1, 0, tzinfo=datetime.timezone.utc),
    },
    {
        'title': 'Bảo vệ lá phổi của bạn trước ô nhiễm không khí',
        'slug': 'bao-ve-la-phoi-cua-ban-truoc-o-nhiem-khong-khi',
        'category': 'news',
        'summary': 'Những khuyến cáo quan trọng từ các bác sĩ chuyên khoa hô hấp.',
        'content': (
            'Theo dõi chất lượng không khí và hạn chế hoạt động ngoài trời khi mức ô nhiễm cao là những biện pháp thiết thực để bảo vệ hệ hô hấp.\n\n'
            'Người cao tuổi, trẻ nhỏ và người đang mắc bệnh hô hấp mạn tính cần đặc biệt chú ý các biểu hiện khó thở, ho tăng hoặc tức ngực và đi khám khi cần thiết.'
        ),
        'cover_image_url': './assets/images/news-2.png',
        'status': 'published',
        'is_featured': False,
        'published_at': datetime.datetime(2024, 4, 10, 1, 0, tzinfo=datetime.timezone.utc),
    },
    {
        'title': 'Bệnh viện tổ chức khám sàng lọc bệnh phổi miễn phí cho người dân',
        'slug': 'benh-vien-to-chuc-kham-sang-loc-benh-phoi-mien-phi-cho-nguoi-dan',
        'category': 'news',
        'summary': 'Nhiều người dân được tư vấn, khám và hướng dẫn chăm sóc sức khỏe hô hấp.',
        'content': (
            'Chương trình khám sàng lọc góp phần nâng cao nhận thức về sức khỏe hô hấp và hỗ trợ phát hiện sớm các trường hợp có nguy cơ.\n\n'
            'Thông tin về các đợt khám tiếp theo sẽ được bệnh viện cập nhật trong mục Thông báo.'
        ),
        'cover_image_url': './assets/images/news-3.png',
        'status': 'published',
        'is_featured': False,
        'published_at': datetime.datetime(2024, 4, 8, 1, 0, tzinfo=datetime.timezone.utc),
    },
]


def seed_posts(apps, schema_editor):
    NewsPost = apps.get_model('news', 'NewsPost')
    for item in POSTS:
        NewsPost.objects.update_or_create(slug=item['slug'], defaults=item)


def remove_seed_posts(apps, schema_editor):
    NewsPost = apps.get_model('news', 'NewsPost')
    NewsPost.objects.filter(slug__in=[item['slug'] for item in POSTS]).delete()


class Migration(migrations.Migration):
    dependencies = [('news', '0001_initial')]
    operations = [migrations.RunPython(seed_posts, remove_seed_posts)]
