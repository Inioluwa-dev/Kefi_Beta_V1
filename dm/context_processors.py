from .models import Message

def unread_dm_count(request):
    if request.user.is_authenticated:
        return {
            'unread_dm_count': Message.objects.filter(recipient=request.user, is_read=False).count()
        }
    return {'unread_dm_count': 0} 