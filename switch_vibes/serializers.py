from rest_framework import serializers

from switch_vibes.yt_to_spotify import get_yt_id_from_url, get_yt_playlist, convert_yt_to_spotify
from switch_vibes.spotify_to_yt import get_spotify_id_from_url, get_spotify_playlist, convert_spotify_to_yt


class YtToSpotifyTrackSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    artists = serializers.ListField(read_only=True)
    year = serializers.CharField(read_only=True)
    duration = serializers.IntegerField(read_only=True)
    uri = serializers.CharField(read_only=True)
    flagged = serializers.BooleanField(read_only=True)


class YtToSpotifySerializer(serializers.Serializer):
    yt_playlist_url = serializers.URLField(required=True, write_only=True, help_text="The URL of the YouTube playlist to be converted to Spotify.")

    def validate(self, data):
        yt_playlist_url = data.get("yt_playlist_url")

        if not yt_playlist_url:
            raise serializers.ValidationError({"error": "yt_playlist_url is required."})
        
        yt_id = get_yt_id_from_url(yt_playlist_url)

        if not yt_id:
            raise serializers.ValidationError({"error": "Invalid YouTube playlist URL."})
        
        yt_playist = get_yt_playlist(yt_id)

        if not yt_playist:
            raise serializers.ValidationError({"error": "Sorry an error occured. Please try again soon."})

        if "404" in yt_playist:
            raise serializers.ValidationError({"error": "The requested playlist could not be found on YT Music."})
        
        data["yt_playist"] = yt_playist
        return data
    
    def create(self, validated_data):
        yt_playist = validated_data.get("yt_playist")
        new_spotify_playlist = convert_yt_to_spotify(yt_playist["tracks"], yt_playist["title"])
        return new_spotify_playlist


class YtToSpotifyResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new Spotify playlist that was created.")
    spotify_playlist = YtToSpotifyTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)


class SpotifyToYtTrackSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    artists = serializers.ListField(read_only=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    yt_id = serializers.CharField(read_only=True)
    yt_url = serializers.URLField(read_only=True)
    flag = serializers.BooleanField(read_only=True)


class  SpotifyToYtSerializer(serializers.Serializer):
    spotify_playlist_url = serializers.URLField(required=True, write_only=True, help_text="The URL of the Spotify playlist to be converted to YouTube.")

    def validate(self, data):
        spotify_playlist_url = data.get("spotify_playlist_url")

        if not spotify_playlist_url:
            raise serializers.ValidationError({"error": "spotify_playlist_url is required."})
        
        spotify_id = get_spotify_id_from_url(spotify_playlist_url)

        if not spotify_id:
            raise serializers.ValidationError({"error": "Invalid Spotify playlist URL."})
        
        spotify_playist = get_spotify_playlist(spotify_id)

        if not spotify_playist:
            raise serializers.ValidationError({"error": "Sorry an error occured. Please try again soon."})

        if "404" in spotify_playist:
            raise serializers.ValidationError({"error": "The requested playlist could not be found on Spotify."})
        
        data["spotify_playist"] = spotify_playist
        return data
    
    def create(self, validated_data):
        spotify_playist = validated_data.get("spotify_playist")
        new_yt_playlist = convert_spotify_to_yt(spotify_playist)
        return new_yt_playlist
    

class SpotifyToYtResponseSerializer(serializers.Serializer):
    """This serializer is just used for Swagger documentation."""
    link = serializers.URLField(read_only=True, help_text="The URL of the new YouTube playlist that was created.")
    yt_playlist = SpotifyToYtTrackSerializer(many=True, read_only=True)
    nulls = serializers.ListField(read_only=True)
    flagged = serializers.ListField(read_only=True)
