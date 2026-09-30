from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import NewsPost, NewsImage


def published_posts():
    return NewsPost.objects.filter(
        status=NewsPost.Status.PUBLISHED,
        published_at__isnull=False,
        published_at__lte=timezone.now(),
    )


def serialize_post(post, include_content=False):
    item = {
        'title': post.title,
        'slug': post.slug,
        'category': post.category,
        'categoryLabel': post.get_category_display(),
        'summary': post.summary,
        'coverImage': post.cover_image_url,
        'isFeatured': post.is_featured,
        'publishedAt': post.published_at.isoformat(),
        'updatedAt': post.updated_at.isoformat(),
    }
    if include_content:
        item['content'] = post.content
    return item


@require_GET
def news_list(request):
    queryset = published_posts()
    category = request.GET.get('category', '').strip()
    search = request.GET.get('q', '').strip()[:100]

    if category in {NewsPost.Category.NEWS, NewsPost.Category.ANNOUNCEMENT}:
        queryset = queryset.filter(category=category)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(summary__icontains=search) | Q(content__icontains=search)
        )

    try:
        limit = int(request.GET.get('limit', 30))
    except (TypeError, ValueError):
        limit = 30
    limit = min(max(limit, 1), 50)
    items = [serialize_post(post) for post in queryset[:limit]]
    return JsonResponse({'success': True, 'count': len(items), 'items': items})


@require_GET
def news_detail(request, slug):
    post = published_posts().filter(slug=slug).first()
    if not post:
        return JsonResponse(
            {'success': False, 'message': 'Không tìm thấy bài viết hoặc bài viết chưa được xuất bản.'},
            status=404,
        )
    return JsonResponse({'success': True, 'item': serialize_post(post, include_content=True)})


@csrf_exempt
@require_http_methods(["POST"])
def upload_image(request):
    uploaded_file = request.FILES.get('image') or request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'success': False, 'message': 'Vui lòng chọn tập tin hình ảnh.'}, status=400)

    import os
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
    if ext not in allowed_extensions:
        return JsonResponse({
            'success': False,
            'message': f'Định dạng tệp không được hỗ trợ ({ext}). Chỉ chấp nhận: JPG, PNG, WEBP, GIF, SVG.'
        }, status=400)

    if uploaded_file.size > 15 * 1024 * 1024:
        return JsonResponse({'success': False, 'message': 'Dung lượng ảnh vượt quá giới hạn 15MB.'}, status=400)

    post_id = request.POST.get('post_id')
    post = None
    if post_id:
        try:
            post = NewsPost.objects.filter(pk=int(post_id)).first()
        except (ValueError, TypeError):
            pass

    caption = request.POST.get('caption', '').strip()[:255]
    img = NewsImage.objects.create(post=post, image=uploaded_file, caption=caption)

    return JsonResponse({
        'success': True,
        'id': img.id,
        'url': img.image.url,
        'caption': img.caption,
        'name': uploaded_file.name
    })


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def image_item(request, image_id):
    img = NewsImage.objects.filter(pk=image_id).first()
    if not img:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy hình ảnh.'}, status=404)

    if request.method == 'DELETE':
        if img.image:
            try:
                img.image.delete(save=False)
            except Exception:
                pass
        img.delete()
        return JsonResponse({'success': True, 'message': 'Đã xóa hình ảnh.'})

    return JsonResponse({
        'success': True,
        'item': {
            'id': img.id,
            'url': img.image.url,
            'caption': img.caption,
            'createdAt': img.created_at.isoformat()
        }
    })


@require_GET
def image_list(request):
    post_id = request.GET.get('post_id')
    qs = NewsImage.objects.all().order_by('-created_at')
    if post_id:
        try:
            qs = qs.filter(post_id=int(post_id))
        except (ValueError, TypeError):
            pass
    items = [
        {
            'id': img.id,
            'url': img.image.url,
            'caption': img.caption,
            'createdAt': img.created_at.isoformat(),
            'postId': img.post_id
        }
        for img in qs[:50]
    ]
    return JsonResponse({'success': True, 'items': items})

