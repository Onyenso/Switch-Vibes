import json
from spotipy import Spotify, SpotifyClientCredentials, SpotifyOAuth


REDIRECT_URI = "http://example.com"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIPY_CLIENT_ID = "5d8fbc87cec540c19658832aaed3c9a3"
SPOTIPY_CLIENT_SECRET = "246ca82970fe482eaa4c6c0a2500aa05"

scope = ["playlist-modify-private", "playlist-modify-public"]

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
# auth_manager = SpotifyOAuth(
#     client_id=SPOTIPY_CLIENT_ID,
#     client_secret=SPOTIPY_CLIENT_SECRET,
#     scope=scope, redirect_uri=REDIRECT_URI
# )

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

def search_for_spotify_track(query, artist, duration):
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
            "duration_seconds": 210,
            "year": 2021,
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

        # Check that artist for given track is the same artist that is gotten and
        # check that duration difference is not greater than 5 seconds.
        if track["artists"][0]["name"] == artist and abs(track_duration_seconds - duration) <= 5:
            track_url = track["external_urls"]["spotify"]
            # add track to list
            track_results.append({
                "title": track["name"],
                "artists": [artist["name"] for artist in track["artists"]],
                "duration_seconds": track_duration_seconds,
                "year": track_year,
                "track_url": track_url
            })

            # Add a break statement here to prevent further iteration after track has been found.
            # break

    return track_results[0] if len(track_results) > 0 else None


def convert_yt_to_spotify(yt_playlist):
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
        "year": 2022 || null,
        "duration_seconds": 230
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
    spotipy_playlist = []

    for track in yt_playlist:

        artists = ""

        for artist in track["artists"]:
            artists += artist + " "

        artists = artists.strip()

        # E.g. Miss You Bad Mr Eazi Burna Boy
        q = f"{track['title']} {artists}"
        print(q)

        sp_track = search_for_spotify_track(q, track["artists"][0], track["duration_seconds"])
        spotipy_playlist.append(sp_track)

    return spotipy_playlist



# TODO
# Find out why Null is being returned for some yt tracks when searched on Spotify. ✅
# Confirm that Holy Holy was in the first 50 that was returned from Spotify search. ✅
# Retrive a song that has a video from YT Music and confirm if the duration are different from noraml audio. ✅
# Rewrite the way you parse song details in convert_yt_to_spotify() in order to march the incoming details
# from get_yt_playlist() accurately. ✅

# REITERATIONS:
# (Check that artist for given track is the same artist that is gotten and
# check that duration difference is not greater than 5 seconds) OR that if song is a video, duration is not more
# than 15 seconds difference.

# Figure out a way to utilize all the artists in the list of artists of a track from YT Music when
# checking the condition of comparism between YT Music and Spotify (in def search_for_spotify_track). Right now you're
# just checking for the first artist from the list.

# Also figure out a way to utilze year during comparism. Right now, you're not making use of it.

# How to check nulls:
# 1) Check for song title in YT Music JSON playlist
# 2) Copy query that was used to serach for song from terminal.
# 3) Paste query in Spotify search API console.
# 4) Copy respoonse and paste in JSON viewer.
# 5) Inspect artist name to make sure they match.
# 6) If artist name match, compare song duration with YT Music song duration.
# 7) If duration dont match, get videoID of song from raw_yt_playlist.json.
# 8) yt.get_song() details of song and confirm if song was a video.
# 9) Document your findings.
