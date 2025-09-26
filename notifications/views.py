from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification 

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(to_user=request.user).order_by('-timestamp')
    return render(request, 'notifications/notifications_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, to_user=request.user)
    notification.is_read = True
    notification.save()
    # Redirect to the relevant post or page
    if notification.notification_type == 'report' and notification.post:
        # Owner can view blocked post via notification link
        return redirect(f"{notification.post.get_absolute_url()}?from_notification=1")
    elif notification.notification_type in ['like', 'comment'] and notification.post:
        return redirect('posts:post_detail', pk=notification.post.pk)
    # Add more types as needed
    return redirect('notifications:list')

@login_required
def notification_count_api(request):
    """API endpoint to get unread notification count"""
    count = Notification.objects.filter(to_user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(to_user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read!')
    return redirect('notifications:list')