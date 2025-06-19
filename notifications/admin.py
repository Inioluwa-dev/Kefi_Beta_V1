from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'to_user', 'from_user', 'notification_type', 'is_read', 'timestamp')
    search_fields = ('to_user__username', 'from_user__username', 'notification_type')
    list_filter = ('notification_type', 'is_read', 'timestamp')
