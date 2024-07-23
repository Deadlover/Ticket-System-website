from django.urls import path
from . import consumers

websocket_urlpatterns=[
    path('ws/sc/<str:groupname>/<int:hall>',consumers.UpdateRealtime.as_asgi()),
    # path('ws/as/',consumers.UpdateRealTime.as_asgi()),
]