# from django.db import models
# from django.contrib.auth.models import User
# from .models import Post

# class Report(models.Model):
#     REPORT_TYPE_CHOICES = [
#         ('post', 'Post'),
#         ('user', 'User'),
#     ]
#     reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
#     reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_received', null=True, blank=True)
#     reported_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
#     report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
#     reason = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_resolved = models.BooleanField(default=False)

#     def __str__(self):
#         if self.report_type == 'post':
#             return f"{self.reporter} reported post {self.reported_post.id}"
#         else:
#             return f"{self.reporter} reported user {self.reported_user.username}"
