from django.urls import path
from . import views
from .views import user_exists_view

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('follow/<str:username>/', views.follow_view, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_view, name='unfollow'),
    path('deactivate/', views.deactivate_account_view, name='deactivate_account'),
    path('delete/', views.delete_account_view, name='delete_account'),
    path('settings/', views.settings_view, name='settings'),
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_of_service_view, name='terms_of_service'),
    path('cookies/', views.cookie_policy_view, name='cookie_policy'),
    path('ajax/send_verification_code/', views.send_verification_code, name='send_verification_code'),
    path('ajax/verify_code/', views.verify_code, name='verify_code'),
]

urlpatterns += [
    path('exists/', user_exists_view, name='user_exists'),
]
