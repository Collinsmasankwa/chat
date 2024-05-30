from django.urls import path
from .consumers import ChatConsumer, MessageTypingConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:username>/<str:room_name>/', ChatConsumer.as_asgi()),
    path('ws/textarea/<str:username>/<str:room_name>/', MessageTypingConsumer.as_asgi()),
]
