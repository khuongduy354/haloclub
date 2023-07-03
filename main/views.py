from pytube import YouTube
from django.conf import os, settings
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
import re
from helpers.get_abs_path import get_abs_path


def parse_range_header(range_header, file_size):
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(
        2) else file_size - 1
    return start, end


def download_video(video_id):
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    yt = YouTube(youtube_url)

    stream = yt.streams.get_highest_resolution()
    if not stream:
        return False

    file_path = get_abs_path("/statics/"+stream.default_filename)
    stream.download(file_path)


def stream_video(request):
    video_id = request.GET.get('video_id')
    if not video_id:
        return HttpResponse(b"No video id", status=400)
    video = download_video(video_id)
    if not video:
        return HttpResponse(b"Cant download video", status=500)

    video_path = os.path.join(settings.MEDIA_ROOT, 'video.mp4')
    range_header = request.META.get('HTTP_RANGE', '').strip()

    video_file = open(video_path, 'rb')
    file_size = os.path.getsize(video_path)

    response = FileResponse(video_file, content_type='video/mp4')
    response['Content-Disposition'] = 'inline; filename="video.mp4"'

    if range_header:
        start, end = parse_range_header(range_header, file_size)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(end - start + 1)
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response.status_code = 206
        video_file.seek(start)
        return response

    return response
# Create your views here.
