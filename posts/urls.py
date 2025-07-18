from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('feed/', views.feed_view, name='feed'),
    path('feed/api/', views.feed_api_view, name='feed_api'),
    path('create/', views.post_create_view, name='post_create'),
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    path('<int:pk>/like/', views.like_post_view, name='like_post'),
    path('<int:post_id>/report/', views.report_post_view, name='report_post'),
    path('user/<str:username>/report/', views.report_user_view, name='report_user'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/block_post/<int:post_id>/', views.block_post_view, name='block_post'),
    path('admin/unblock_post/<int:post_id>/', views.unblock_post_view, name='unblock_post'),
]
