from django.urls import path
from .views import stream_video

urlpatterns = [
    path("", stream_video, name="stream_video")
]
