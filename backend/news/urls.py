from django.urls import path

from . import views


urlpatterns = [
    path('', views.news_list, name='news-list'),
    path('upload-image/', views.upload_image, name='news-upload-image'),
    path('images/', views.image_list, name='news-image-list'),
    path('images/<int:image_id>/', views.image_item, name='news-image-item'),
    path('<slug:slug>/', views.news_detail, name='news-detail'),
]

