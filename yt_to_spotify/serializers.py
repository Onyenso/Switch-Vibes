from rest_framework import serializers


class YtToSpotifyTrackSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    artists = serializers.ListField(read_only=True)
    year = serializers.CharField(read_only=True)
    duration = serializers.IntegerField(read_only=True)
    uri = serializers.CharField(read_only=True)
    flagged = serializers.BooleanField(read_only=True)


class YtToSpotifySerializer(serializers.Serializer):
    yt_playlist_url = serializers.URLField(
        required=True,
        write_only=True,
        help_text="The URL of the YouTube playlist to be converted to Spotify."
    )


class YtToSpotifyResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new Spotify playlist that was created.")
    playlist = YtToSpotifyTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)
