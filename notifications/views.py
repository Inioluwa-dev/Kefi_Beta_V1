from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
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