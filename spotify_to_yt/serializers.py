from rest_framework import serializers

from spotify_to_yt.spotify_to_yt import get_spotify_id_from_url, get_spotify_playlist, convert_spotify_to_yt


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

    def validate(self, data):
        spotify_playlist_url = data.get("spotify_playlist_url")

        if not spotify_playlist_url:
            raise serializers.ValidationError({"error": "spotify_playlist_url is required."})
        
        spotify_id = get_spotify_id_from_url(spotify_playlist_url)

        if not spotify_id:
            raise serializers.ValidationError({"error": "Invalid Spotify playlist URL."})
        
        spotify_playlist = get_spotify_playlist(spotify_id)

        if not spotify_playlist:
            raise serializers.ValidationError({"error": "Sorry an error occurred. Please try again soon."})

        if "404" in spotify_playlist:
            raise serializers.ValidationError({"error": "The requested playlist could not be found on Spotify."})
        
        data["spotify_playlist"] = spotify_playlist
        return data
    
    def create(self, validated_data):
        spotify_playlist = validated_data.get("spotify_playlist")
        new_yt_playlist = convert_spotify_to_yt(spotify_playlist)
        return new_yt_playlist
    

class SpotifyToYtResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new YouTube playlist that was created.")
    playlist = SpotifyToYtTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)
