from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import APIView
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from switch_vibes.serializers import YtToSpotifySerializer, YtToSpotifyResponseSerializer, SpotifyToYtSerializer, SpotifyToYtResponseSerializer


def index(request):
    return HttpResponse("Hello World! Welcome to Switch Vibes! The server is running.")


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["YT to Spotify"],
        operation_id="yt_to_spotify",
        operation_description="Convert a YouTube playlist to a Spotify playlist.",
        request_body=YtToSpotifySerializer(),
        responses={200: YtToSpotifyResponseSerializer}
    )
)
class YtToSpotify(APIView):
    def post(self, request, format=None):
        serializer = YtToSpotifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_spotify_playlist = serializer.save()
        return Response(new_spotify_playlist, status=200)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Spotify to YT"],
        operation_id="spotify_to_yt",
        operation_description="Convert a Spotify playlist to a YouTube playlist.",
        request_body=SpotifyToYtSerializer(),
        responses={200: SpotifyToYtResponseSerializer}
    )
)
class SpotifyToYt(APIView):
    def post(self, request, format=None):
        serializer = SpotifyToYtSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_yt_playlist = serializer.save()
        return Response(new_yt_playlist, status=200)
