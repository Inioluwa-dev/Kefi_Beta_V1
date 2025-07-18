from django.db import models
from django.contrib.auth.models import User
from PIL import Image

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_pic:
            img = Image.open(self.profile_pic.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_pic.path)
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 600 or img.width > 1200:
                output_size = (1200, 600)
                img.thumbnail(output_size)
                img.save(self.cover_image.path)