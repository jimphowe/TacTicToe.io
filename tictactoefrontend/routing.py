from django.urls import re_path
from .consumers import GameConsumer, SetupConsumer

websocket_urlpatterns = [
    re_path(r'ws/game/(?P<game_code>[A-Z0-9]{6})/$', GameConsumer.as_asgi()),
    re_path(r'ws/setup/$', SetupConsumer.as_asgi()),
]