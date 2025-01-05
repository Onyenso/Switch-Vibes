from rest_framework import serializers


class SpotifyToYtTrackSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    artists = serializers.ListField(read_only=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    yt_id = serializers.CharField(read_only=True)
    yt_url = serializers.URLField(read_only=True)
    flag = serializers.BooleanField(read_only=True)


class  SpotifyToYtSerializer(serializers.Serializer):
    spotify_playlist_url = serializers.URLField(
        required=True,
        write_only=True,
        help_text="The URL of the Spotify playlist to be converted to YouTube."
    )


class SpotifyToYtResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new YouTube playlist that was created.")
    playlist = SpotifyToYtTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)
