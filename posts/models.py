from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
import re
from io import BytesIO
from django.core.files.base import ContentFile

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=500)
    image = models.ImageField(upload_to='post_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Order posts by creation date (newest first)
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                buffer = BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img.save(buffer, format=img_format)
                buffer.seek(0)
                self.image.save(self.image.name, ContentFile(buffer.read()), save=False)
        super().save(*args, **kwargs)

    def get_hashtags(self):
        return re.findall(r'#(\w+)', self.content)

    def get_mentions(self):
        return re.findall(r'@(\w+)', self.content)
    
    def get_absolute_url(self):
        return reverse('posts:post_detail', args=[str(self.pk)])

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.post.id}: {self.content[:20]}"


class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('user', 'User'),
        ('post', 'Post'),
    )
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_received')
    reported_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_on_post')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    reason = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)  # <-- Add this line
    created_at = models.DateTimeField(auto_now_add=True)