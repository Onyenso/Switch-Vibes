from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import APIView
from rest_framework.response import Response

from spotify_to_yt.serializers import (
    SpotifyToYtSerializer,
    SpotifyToYtResponseSerializer
)


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
