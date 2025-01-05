import json
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import APIView
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from yt_to_spotify.serializers import (
    YtToSpotifySerializer,
    YtToSpotifyResponseSerializer,
)
from yt_to_spotify.services import YtToSpotifyService
from asgiref.sync import async_to_sync


def index(request):
    return HttpResponse("Hello World! Welcome to SwitchVibes! The server is running.")


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
        data = json.dumps(request.data)
        result = async_to_sync(YtToSpotifyService.handle_yt_to_spotify)(data)
        return Response(result)
