"""This file converts Spotify to YT."""

import json
from spotipy import Spotify, SpotifyClientCredentials, SpotifyOAuth

SPOTIFY_REDIRECT_URI = "http://example.com"
SPOTIFY_BASE_URL = "https://api.spotify.com/v1"
SPOTIPY_CLIENT_ID = "5d8fbc87cec540c19658832aaed3c9a3"
SPOTIPY_CLIENT_SECRET = "246ca82970fe482eaa4c6c0a2500aa05"
SPOTIFY_ID = "31zqj4xzqxbsxjlyggys73k3c4my"

spotify_scope = ["playlist-modify-private", "playlist-modify-public"]

auth_manager = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    scope=spotify_scope, redirect_uri=SPOTIFY_REDIRECT_URI,
    show_dialog=True,
)

sp = Spotify(auth_manager=auth_manager)


def get_spotify_playlist(playlist_id):
    """
    Get's a Spotify playlist's raw data and pareses it.
    """
    
    # Get the first 100 tracks from playlist
    parsed_playlist_tracks = sp.playlist(
        playlist_id=playlist_id,
        fields="id,name,tracks.items(track(name,artists(name),duration_ms)),tracks.next",
    )

    next = parsed_playlist_tracks["tracks"]["next"]
    offset = 0

    # Get the remaining tracks
    while next is not None:
        offset += 100

        next_tracks = sp.playlist_items(
            playlist_id=playlist_id,
            fields="items(track(name,artists(name),duration_ms)),next",
            offset=offset
        )

        parsed_playlist_tracks["tracks"]["items"].extend(next_tracks["items"])
        next = next_tracks["next"]
        parsed_playlist_tracks["tracks"]["next"] = next

    return parsed_playlist_tracks

# jamming of genitals
id1 = "5KegusCFrx118JomSBcjvD"
# url1 = "https://open.spotify.com/playlist/5KegusCFrx118JomSBcjvD?si=cf777c0869a24c5"

# R & B
id2 = "3AyRHA5JC0QtHWHhdph1fb"
# url2 = https://open.spotify.com/playlist/3AyRHA5JC0QtHWHhdph1fb?si=44cc73ec9e444762

# AlphaDev's Playlist
id3 = "0Mpj7oqduJ24uMGy5tC8ff"
# url3 = "https://open.spotify.com/playlist/0Mpj7oqduJ24uMGy5tC8ff?si=505779dcd2ca4e6e"

spotify_playlist = get_spotify_playlist(id3)

with open("spotify_to_yt_jsons/result.json", "w") as file:
    json.dump(spotify_playlist, file,indent=4)

print('Done.')



# result = sp.search(q=f"track:All I Need (feat. Wale) artist:Chris Brown", type="track")
# result = sp.search(q=f"Non Living Things Sarkodie Ft.Oxlade", type="track")
# print(result)

# TODO
# Clean up code