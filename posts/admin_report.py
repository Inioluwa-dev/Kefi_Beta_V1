from django.contrib import admin
from .report import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'report_type', 'reported_user', 'reported_post', 'is_resolved', 'timestamp')
    search_fields = ('reporter__username', 'reported_user__username', 'reported_post__content')
    list_filter = ('report_type', 'is_resolved', 'timestamp')
