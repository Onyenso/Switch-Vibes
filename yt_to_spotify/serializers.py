from rest_framework import serializers

from yt_to_spotify.yt_to_spotify import get_yt_id_from_url, get_yt_playlist, convert_yt_to_spotify


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

    def validate(self, data):
        yt_playlist_url = data.get("yt_playlist_url")

        if not yt_playlist_url:
            raise serializers.ValidationError({"error": "yt_playlist_url is required."})
        
        yt_id = get_yt_id_from_url(yt_playlist_url)

        if not yt_id:
            raise serializers.ValidationError({"error": "Invalid YouTube playlist URL."})
        
        yt_playlist = get_yt_playlist(yt_id)

        if not yt_playlist:
            raise serializers.ValidationError({"error": "Sorry an error occurred. Please try again soon."})

        if "404" in yt_playlist:
            raise serializers.ValidationError({"error": "The requested playlist could not be found on YT Music."})
        
        data["yt_playlist"] = yt_playlist
        return data
    
    def create(self, validated_data):
        yt_playlist = validated_data.get("yt_playlist")
        new_spotify_playlist = convert_yt_to_spotify(yt_playlist["tracks"], yt_playlist["title"])
        return new_spotify_playlist


class YtToSpotifyResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new Spotify playlist that was created.")
    playlist = YtToSpotifyTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)
