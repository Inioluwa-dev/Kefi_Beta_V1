from django.contrib import admin
from .models import Post, Like, Comment, Report

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'content', 'created_at')
    search_fields = ('user__username', 'content', 'post__content')
    list_filter = ('created_at',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'reporter', 'reported_user', 'reported_post', 'reason', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('reporter__username', 'reported_user__username', 'reported_post__id', 'reason')