from django.contrib import admin
from django.utils.html import format_html

from .models import NewsPost, NewsImage


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 0
    fields = ('image', 'caption', 'image_preview', 'created_at')
    readonly_fields = ('image_preview', 'created_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; object-fit: cover; box-shadow: 0 1px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Xem trước'


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'published_at', 'updated_at')
    list_filter = ('status', 'category', 'is_featured', 'published_at')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'
    inlines = [NewsImageInline]
    fieldsets = (
        ('Nội dung', {'fields': ('title', 'slug', 'category', 'summary', 'content')}),
        ('Hiển thị', {'fields': ('cover_image_url', 'status', 'is_featured', 'published_at')}),
        ('Hệ thống', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    class Media:
        css = {
            'all': ('news/admin_article_editor.css',)
        }
        js = ('news/admin_article_editor.js',)


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'caption', 'post', 'created_at')
    search_fields = ('caption', 'post__title')
    list_filter = ('created_at',)
    readonly_fields = ('image_preview', 'created_at')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; object-fit: cover;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Hình ảnh'

