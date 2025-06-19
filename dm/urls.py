from django.urls import path
from . import views

app_name = 'dm'

urlpatterns = [
    path('inbox/', views.inbox_view, name='inbox'),
    path('send/', views.send_message_view, name='send'),
    path('thread/<str:username>/', views.thread_view, name='thread'),
]
