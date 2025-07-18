from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<username>\w+)/?$', consumers.DMConsumer.as_asgi()),
] 