from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'followers_count', 'following_count')
    search_fields = ('user__username', 'location')

# Register your models here.
