from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    cover_image = models.ImageField(upload_to='profile_covers/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    # Users this profile is following
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    links = models.TextField(blank=True)  # Comma-separated or JSON links
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def get_profile_pic_url(self):
        """Get profile picture signed URL with fallback to static default"""
        if self.profile_pic and hasattr(self.profile_pic, 'name') and self.profile_pic.name != 'profile_pics/default.jpg':
            try:
                from utils.b2_signed_url import generate_b2_signed_url
                return generate_b2_signed_url(self.profile_pic.name)
            except Exception:
                pass
        return '/static/users/default-profile.jpg'

    def get_cover_image_url(self):
        """Get cover image signed URL or None if not set"""
        if self.cover_image and hasattr(self.cover_image, 'name') and self.cover_image.name:
            try:
                from utils.b2_signed_url import generate_b2_signed_url
                return generate_b2_signed_url(self.cover_image.name)
            except Exception:
                pass
        return None

    def save(self, *args, **kwargs):
        # Resize profile_pic in-memory
        if self.profile_pic and hasattr(self.profile_pic, 'file') and self.profile_pic.name != 'profile_pics/default.jpg':
            try:
                img = Image.open(self.profile_pic)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    buffer = BytesIO()
                    img_format = img.format if img.format else 'JPEG'
                    img.save(buffer, format=img_format)
                    buffer.seek(0)
                    self.profile_pic.save(self.profile_pic.name, ContentFile(buffer.read()), save=False)
            except Exception:
                pass
        # Resize cover_image in-memory
        if self.cover_image and hasattr(self.cover_image, 'file'):
            try:
                img = Image.open(self.cover_image)
                if img.height > 600 or img.width > 1200:
                    output_size = (1200, 600)
                    img.thumbnail(output_size)
                    buffer = BytesIO()
                    img_format = img.format if img.format else 'JPEG'
                    img.save(buffer, format=img_format)
                    buffer.seek(0)
                    self.cover_image.save(self.cover_image.name, ContentFile(buffer.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)