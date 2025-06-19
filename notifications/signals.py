from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Like, Comment, Post
from users.models import Profile
from .models import Notification

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.post.user != instance.user:
        Notification.objects.create(
            to_user=instance.post.user,
            from_user=instance.user,
            notification_type='like',
            post=instance.post
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.post.user != instance.user:
        Notification.objects.create(
            to_user=instance.post.user,
            from_user=instance.user,
            notification_type='comment',
            post=instance.post,
            comment=instance
        )
