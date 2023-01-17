import json
from spotipy import Spotify, SpotifyClientCredentials, SpotifyOAuth
from utils import string_similarity, list_similarity

REDIRECT_URI = "http://example.com"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIPY_CLIENT_ID = "5d8fbc87cec540c19658832aaed3c9a3"
SPOTIPY_CLIENT_SECRET = "246ca82970fe482eaa4c6c0a2500aa05"
MY_SPOTIFY_ID = "31zqj4xzqxbsxjlyggys73k3c4my"

scope = ["playlist-modify-private", "playlist-modify-public"]

# auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    scope=scope, redirect_uri=REDIRECT_URI,
    show_dialog=True,
)

sp = Spotify(auth_manager=auth_manager)


"""Will be used for Spotify to YT Music conversion"""
def get_spotify_playlist(playlist_id):
    playlist = sp.playlist_items(
        playlist_id=playlist_id, limit=100,
        fields="items.track.name,items.track.artists.name",
        # fields="tracks.items.track.name,tracks.items.track.artists.name"
    )

    return playlist


# example_spotify_playlist_url = https://open.spotify.com/playlist/3AyRHA5JC0QtHWHhdph1fb?si=44cc73ec9e444762
# spotify_playlist = get_spotify_playlist("3AyRHA5JC0QtHWHhdph1fb")

def search_for_spotify_track(query, artists, duration, video):
    """
    Searches for a track on Spotify using title, artist and duration of track
    and returns a dictionary with the track's details if found, else returns None.

    :param query: a string representing the title of track (or whatever string you
    wanna search for on Spotify), or part of the title.
    :param artist: a string representing the name of artist, or part of the name.
    :param duration: an integer representing the duration of track in seconds.

    :return track_details: a dictionary with the details of the track, if found on Spotify,
    else None. Example of the dictionary when track is found:
    E.g. of a dictionary in the list:
    {
            "title": "Wine",
            "artists": ["Rema", "Yseult"],
            "year": 2021,
            "duration_seconds": 210,
            "track_url": "https://open.spotify.com/track/2qpCxK7imR1qbH4fbdgWLg"
    }
    """
    track_results = []

    # Search for track on Spotify
    response = sp.search(query, type="track", limit=5)

    # Parse results to get the right track details
    for track in response["tracks"]["items"]:
        track_duration_seconds = int(track["duration_ms"] / 1000)
        track_year = int(track["album"]["release_date"][:4])

        sp_artists = [artist["name"].lower() for artist in track["artists"]]

        correct_artist = bool(
            string_similarity(artists[0], sp_artists[0]) >= 0.4 or \
            list_similarity(artists, sp_artists) >= 1 / max(len(artists), len(sp_artists)) or \
            string_similarity(str(artists), str(sp_artists)) >= 0.4
        )

       


        if (correct_artist and abs(track_duration_seconds - duration) <= 5) or \
        (video and correct_artist and abs(track_duration_seconds - duration) <= 90):

            track_url = track["external_urls"]["spotify"]

            track_results.append({
                "title": track["name"],
                "artists": [artist["name"] for artist in track["artists"]],
                "year": track_year,
                "duration_seconds": track_duration_seconds,
                "track_url": track_url,
                "uri": track["uri"]
            })

            # To prevent futher iteration after track has been found
            break
    return track_results[0] if len(track_results) > 0 else None


def convert_yt_to_spotify(yt_playlist, name):
    """
    Accepts a list of dictionaries where each dictionary represents a
    track in a parsed YT Music playlist, and then searches for each of
    the tracks on Spotify. It returns a list of dictionaries of the tracks
    found on Spotify.

    :param yt_playlist: a list of dictionaries. Each dictionary represents a
    track in a YT Music playlist.
    E.g. of a dictionary in the list will look like:
    {
        "title": "Wine",
        "artists": ["Rema"],
        "duration_seconds": 230,
        "year": 2022 || null,
    }
    :return spotipy_playlist: a list of dictionaries. Each dictionary represents a track.
    E.g. of a dictionary in the list:
    {
            "title": "Wine",
            "artists": ["Rema", "Yseult"],
            "duration_seconds": 210,
            "year": 2021,
            "track_url": "https://open.spotify.com/track/2qpCxK7imR1qbH4fbdgWLg"
    }
    """
    parsed_spotify_playlist = []

    for track in yt_playlist:

        artists = ""

        for artist in track["artists"]:
            artists += artist + " "

        artists = artists.strip()

        # E.g. Miss You Bad Mr Eazi Burna Boy
        q = f"{track['title']} {artists}"
        # print(q)

        sp_track = search_for_spotify_track(
            query=q,
            artists=[artist.lower() for artist in track["artists"]],
            duration=int(track["duration_seconds"]),
            video=track["video"]
        )

        parsed_spotify_playlist.append(sp_track)

    spotify_playlist = sp.user_playlist_create(
        user=MY_SPOTIFY_ID,
        name=name,
        public=False,
        description="Generated by Gbedu Links."
    )

    sp.playlist_add_items(
        playlist_id=spotify_playlist["id"],
        items=[track["uri"] for track in parsed_spotify_playlist]
    )

    print("Spotify Playlist:", spotify_playlist["external_urls"]["spotify"])
    return (spotify_playlist)



# TODO
# What should happen for nulls in YT Music??
# What is this about Spotify being able to add just 100 songs at once? Test with AlphaDev's Playlist.
# Clean up code. Seperate functions to different files etc.
# How to permanently grant an app access to my Spotify account

