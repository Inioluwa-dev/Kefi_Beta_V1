from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm
from .views import ReactivatePasswordResetConfirmView

urlpatterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html', form_class=CustomPasswordResetForm), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ReactivatePasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
