from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post, Like, Comment, Report
from .forms import PostForm, CommentForm
from .forms_report import ReportForm
from users.models import Profile
from django.contrib.auth.models import User
from notifications.models import Notification
from kefi_beta_version1.views import custom_404_view
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
import hashlib
import time
from django.utils import timezone

def feed_view(request):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/posts/feed/&login_required=1")
    posts = Post.objects.filter(blocked=False).order_by('-created_at')
    return render(request, 'posts/feed.html', {'posts': posts})

def post_create_view(request):
    if not request.user.is_authenticated:
        return custom_404_view(request)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('posts:feed')
    else:
        form = PostForm()
    
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Check if the post is blocked
    if post.blocked:
        # If the user is admin, allow
        if request.user.is_staff:
            pass
        # If the user is the owner, only allow if coming from notification
        elif request.user == post.user:
            # Check if coming from notification link (e.g., ?from_notification=1)
            if request.GET.get('from_notification') == '1':
                pass  # allow
            else:
                return render(request, 'posts/post_blocked.html', {'post': post})
        else:
            return render(request, 'posts/post_blocked.html', {'post': post})
    comments = post.comments.all().order_by('created_at')
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('posts:post_detail', pk=pk)
    else:
        comment_form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        messages.info(request, 'You unliked the post.')
    else:
        messages.success(request, 'You liked the post!')
    return HttpResponseRedirect(reverse('posts:post_detail', args=[pk]))

@login_required
def report_post_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_post = post
            report.report_type = 'post'
            report.save()
            # Notify all admins
            admins = User.objects.filter(is_staff=True, is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    to_user=admin,
                    from_user=request.user,
                    notification_type='report',
                    post=post,
                    message=f"""
            A post has been reported.

            Post ID: {post.pk}
            Author: @{post.user.username}
            Reported by: @{request.user.username}
            Reason: {report.reason}

            Click 'View Full Message' to review the post.
            """
                )
            messages.success(request, 'Post reported. Thank you!')
            return redirect('posts:post_detail', pk=post_id)
    else:
        form = ReportForm()
    return render(request, 'posts/report_post.html', {'form': form, 'post': post})

@login_required
def report_user_view(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = user
            report.report_type = 'user'
            report.save()
            # Notify all admins
            admins = User.objects.filter(is_staff=True, is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    to_user=admin,
                    from_user=request.user,
                    notification_type='report'
                )
            messages.success(request, 'User reported. Thank you!')
            return redirect('users:profile', username=username)
    else:
        form = ReportForm(initial={'reported_user': user, 'report_type': 'user'})
    return render(request, 'posts/report_user.html', {'form': form, 'user_obj': user})

@login_required
def admin_reports_view(request):
    if not request.user.is_staff:
        return redirect('posts:feed')
    reports = Report.objects.filter(report_type='post', resolved=False)
    return render(request, 'posts/admin_reports.html', {'reports': reports})

@login_required
def block_post_view(request, post_id):
    if not request.user.is_staff:
        return redirect('posts:feed')
    post = get_object_or_404(Post, pk=post_id)
    post.blocked = True
    post.save()
    # Mark all related reports as resolved
    Report.objects.filter(reported_post=post, resolved=False).update(resolved=True)
    # Notify post owner
    Notification.objects.create(
        to_user=post.user,
        from_user=request.user,
        notification_type='report',
        post=post,
        message=f"Your post has been blocked by an admin after being reported. Click here to view: {reverse('posts:post_detail', args=[post.pk])}?from_notification=1"
)
    messages.success(request, 'Post has been blocked and the owner notified.')
    return redirect('notifications:list')  # or your admin notifications page


@login_required
def unblock_post_view(request, post_id):
    if not request.user.is_staff:
        return redirect('posts:feed')
    post = get_object_or_404(Post, pk=post_id)
    post.blocked = False
    post.save()
    # Notify post owner
    from notifications.models import Notification
    Notification.objects.create(
        to_user=post.user,
        from_user=request.user,
        notification_type='report',
        post=post,
        message="Your post has been unblocked by an admin and is now visible to everyone."
    )
    messages.success(request, 'Post has been unblocked and the owner notified.')
    return redirect('notifications:list')

def feed_api_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    posts = Post.objects.filter(blocked=False).order_by('-created_at')
    paginator = Paginator(posts, page_size)
    page_obj = paginator.get_page(page)
    html = ''
    count = 0
    for post in page_obj:
        html += render_to_string('posts/post_card.html', {'post': post, 'request': request})
        count += 1
        if count % 5 == 0:
            from django.contrib.auth.models import User
            following = set(request.user.profile.following.values_list('user__id', flat=True))
            suggestions = User.objects.exclude(id__in=following).exclude(id=request.user.id).order_by('?')[:3]
            html += render_to_string('posts/follow_suggestions.html', {
                'suggested_users': suggestions,
                'request': request,
                'following_ids': following,
            })
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
    })