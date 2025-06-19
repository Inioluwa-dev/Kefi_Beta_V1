from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'content', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'recipient__username', 'content')
    list_filter = ('is_read', 'timestamp')
