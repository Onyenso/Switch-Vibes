from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import APIView
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from switch_vibes.publish import respond_to_mentions
from switch_vibes.spotify_to_yt import get_spotify_playlist, convert_spotify_to_yt
from switch_vibes.yt_to_spotify import get_yt_playlist, convert_yt_to_spotify, get_yt_id_from_url


def index(request):
    # respond_to_mentions()
    return HttpResponse("Hello World! Welcome to Switch Vibes! The server is running.")


class YtToSpotify(APIView):
    def post(self, request, format=None):
        yt_playlist_url = request.data.get("yt_playlist_url")

        if not yt_playlist_url:
            return Response({"error": "yt_playlist_url is required."}, status=400)
        
        yt_id = get_yt_id_from_url(yt_playlist_url)

        if not yt_id:
            return Response({"error": "Invalid YouTube playlist URL."}, status=400)
        
        yt_playist = get_yt_playlist(yt_id)

        if not yt_playist:
            return Response({"error": "Sorry an error occured. Please try again soon."}, status=500)

        if "404" in yt_playist:
            return Response({"error": "The requested playlist could not be found on YT Music."}, status=404)
        
        new_spotify_playlist = convert_yt_to_spotify(yt_playist["tracks"], yt_playist["title"])
        return Response(new_spotify_playlist, status=200)


class SpotifyToYt(APIView):
    pass


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=respond_to_mentions, trigger="interval", seconds=3)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())
