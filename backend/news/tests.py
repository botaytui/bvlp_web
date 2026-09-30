from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import NewsPost


class NewsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        NewsPost.objects.all().delete()
        cls.published = NewsPost.objects.create(
            title='Tin sức khỏe hô hấp',
            category=NewsPost.Category.NEWS,
            summary='Tóm tắt bài viết',
            content='Nội dung bài viết.',
            status=NewsPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        NewsPost.objects.create(
            title='Thông báo nội bộ',
            category=NewsPost.Category.ANNOUNCEMENT,
            summary='Không công khai',
            content='Bản nháp.',
            status=NewsPost.Status.DRAFT,
        )

    def test_list_only_returns_published_posts(self):
        response = self.client.get(reverse('news-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_filter_by_category(self):
        response = self.client.get(reverse('news-list'), {'category': 'announcement'})
        self.assertEqual(response.json()['count'], 0)

    def test_search(self):
        response = self.client.get(reverse('news-list'), {'q': 'hô hấp'})
        self.assertEqual(response.json()['count'], 1)

    def test_detail(self):
        response = self.client.get(reverse('news-detail', args=[self.published.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item']['content'], 'Nội dung bài viết.')

    def test_draft_detail_is_hidden(self):
        response = self.client.get(reverse('news-detail', args=['thong-bao-noi-bo']))
        self.assertEqual(response.status_code, 404)
