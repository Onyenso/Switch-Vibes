import json

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import APIView
from rest_framework.response import Response

from spotify_to_yt.serializers import (
    SpotifyToYtSerializer,
    SpotifyToYtResponseSerializer
)
from spotify_to_yt.services import SpotifyToYtService
from asgiref.sync import async_to_sync


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
        data = json.dumps(request.data)
        result = async_to_sync(SpotifyToYtService.handle_spotify_to_yt)(data)
        return Response(result, status=200)
