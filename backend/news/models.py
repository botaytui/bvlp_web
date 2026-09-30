from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class NewsPost(models.Model):
    class Category(models.TextChoices):
        NEWS = 'news', 'Tin tức'
        ANNOUNCEMENT = 'announcement', 'Thông báo'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Bản nháp'
        PUBLISHED = 'published', 'Đã xuất bản'

    title = models.CharField('Tiêu đề', max_length=220)
    slug = models.SlugField('Đường dẫn', max_length=240, unique=True, blank=True)
    category = models.CharField(
        'Phân loại', max_length=20, choices=Category.choices, default=Category.NEWS, db_index=True
    )
    summary = models.CharField('Tóm tắt', max_length=500)
    content = models.TextField('Nội dung')
    cover_image_url = models.CharField(
        'Đường dẫn ảnh đại diện', max_length=300, blank=True,
        help_text='Ví dụ: ./assets/images/news-1.png. Để trống sẽ dùng ảnh mặc định.',
    )
    status = models.CharField(
        'Trạng thái', max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    is_featured = models.BooleanField('Tin nổi bật', default=False, db_index=True)
    published_at = models.DateTimeField('Thời điểm xuất bản', null=True, blank=True, db_index=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật', auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Bài viết'
        verbose_name_plural = 'Bài viết'
        indexes = [
            models.Index(fields=['status', 'published_at'], name='news_status_pub_idx'),
            models.Index(fields=['category', 'published_at'], name='news_cat_pub_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:220] or 'bai-viet'
            candidate = base_slug
            suffix = 2
            while NewsPost.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f'{base_slug[:215]}-{suffix}'
                suffix += 1
            self.slug = candidate
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    post = models.ForeignKey(
        NewsPost,
        on_delete=models.CASCADE,
        related_name='images',
        null=True,
        blank=True,
        verbose_name='Bài viết'
    )
    image = models.FileField('Tập tin ảnh', upload_to='news/%Y/%m/')
    caption = models.CharField('Chú thích ảnh', max_length=255, blank=True)
    created_at = models.DateTimeField('Ngày tải lên', auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Hình ảnh bài viết'
        verbose_name_plural = 'Hình ảnh bài viết'

    def __str__(self):
        return self.caption or self.image.name

