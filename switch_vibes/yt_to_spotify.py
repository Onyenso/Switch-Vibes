"""This file converts YT to Spotify."""
import re
from datetime import datetime
from ytmusicapi import YTMusic
from spotipy import Spotify, SpotifyOAuth
from decouple import config

from switch_vibes.utils import string_similarity, list_similarity
from switch_vibes import constants


spotify_scope = ["playlist-modify-private", "playlist-modify-public"]

auth_manager = SpotifyOAuth(
    client_id=config("SPOTIPY_CLIENT_ID"),
    client_secret=config("SPOTIPY_CLIENT_SECRET"),
    scope=spotify_scope, redirect_uri=config("SPOTIFY_REDIRECT_URI"),
    show_dialog=True,
)

sp = Spotify(auth_manager=auth_manager)
yt = YTMusic()


def get_yt_id_from_url(url):
    """
    Gets the id of a YT Music playlist from its url.

    :param url: a string representing the url of the playlist.

    :return id: a string representing the id of the playlist.
    """
    yt_link = re.findall(constants.YT_MUSIC_REGEX, url)
    if not yt_link: return None
    yt_link = yt_link[0][0]
    yt_music_playlist_id = yt_link.split("?list=")[1].split("&")[0]
    return yt_music_playlist_id


def get_yt_playlist(playlist_id):
    """
    Gets a playlist's raw data from YT Music and parses it and returns a list of dictionaries,
    where each dictionary represents a track from the playlist.

    :param playlist_id: a string representing the id of the playlist.

    :return parsed_playlist_tracks: a list of dictionaries where each dictionary represents a track.
    E.g. of a dictionary in the list might look like:
    {
        "title": "Wine",
        "artists": ["Rema"],
        "year": 2022 || null,
        "duration_seconds": 230
    }
    """
    parsed_playlist_tracks = []

    try:
        playlist = yt.get_playlist(playlistId=playlist_id, limit=None)
    except Exception as e:
        if "404" in str(e):
            parsed_playlist_tracks.append("404")
            return parsed_playlist_tracks
        else: return None
        
    tracks = playlist["tracks"]
    title = playlist["title"]

    print("\n================Searching YT Music========================\n")

    for item in tracks:
        # Get ID of track
        videoID = item["videoId"]
        year = None
        duration_seconds = item.get("duration_seconds")
        
        # Item is a song if videoType == MUSIC_VIDEO_TYPE_ATV or null
        video = False if item["videoType"] == "MUSIC_VIDEO_TYPE_ATV" or not item["videoType"] else True

        # Some tracks have null videoID
        if videoID:
            # Get track data
            music_data = yt.get_song(videoId=videoID)

            # Get release date of track from track data
            published_date = music_data["microformat"]["microformatDataRenderer"]["publishDate"]
            # published_date = datetime.strptime(published_date, '%Y-%m-%d').date()
            published_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%S%z').date()
            year = published_date.year

            # duration gotten from playlist does not match sometimes
            duration_seconds = music_data["videoDetails"]["lengthSeconds"]

        parsed_playlist_tracks.append({
            "title": item["title"],
            "artists": [artists["name"] for artists in item["artists"]],
            "year": year,
            "duration_seconds": int(duration_seconds) if duration_seconds else 0,
            "video": video
        })

        print(f"Found {item['title']} on YT Music...")

    print("\n================YT Music Done========================\n")
    return {"tracks": parsed_playlist_tracks, "title": title}


def convert_yt_to_spotify(yt_playlist, name=None):
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
    
    if "404" in yt_playlist: return ["404"]
    elif not yt_playlist: return None

    parsed_spotify_playlist = []
    nulls = []

    print("\n================Searching Spotify========================\n")

    for track in yt_playlist:
        artists = ""

        for artist in track["artists"]:
            artists += artist + " "

        artists = artists.strip()

        # E.g. Miss You Bad Mr Eazi Burna Boy
        q = f"{track['title']} {artists}"

        sp_track = search_for_spotify_track(
            query=q,
            title=track["title"],
            artists=[artist.lower() for artist in track["artists"]],
            duration=int(track["duration_seconds"]),
            video=track["video"]
        )

        # If track is found, add to parsed playlist else add track to nulls
        parsed_spotify_playlist.append(sp_track) if sp_track else nulls.append({
            "title": track["title"],
            "artists": track["artists"]
        })

    print("\n================Spotify Done========================\n")

    # Create playlist
    spotify_playlist = sp.user_playlist_create(
        user=config("SPOTIFY_ID"),
        name=name,
        public=False,
        description="Generated by Switch Vibes."
    )
    
    # Get uris of tracks from parsed playlist
    uris =[track["uri"] for track in parsed_spotify_playlist]
    start = 0
    stop = 100

    # print("========SPOTIFY PARSED TRACKS========", parsed_spotify_playlist)
    # print("========SPOTIFY PARSED URIS========", uris)
    
    # Add tracks to the created Spotify playlist
    while True:
        sp.playlist_add_items(
            playlist_id=spotify_playlist["id"],
            items=uris[start:stop]
        )
        if stop > len(uris): break
        start = stop
        stop += 100

    data = {
        "link": spotify_playlist["external_urls"]["spotify"],
        "spotify_playlist": parsed_spotify_playlist,
        "nulls": nulls,
        "flagged": [
            {"title": track["title"], "artists": track["artists"]} for \
            track in parsed_spotify_playlist if track["flag"]
        ]
    }

    print(f"Spotify Playlist: {data['link']}\n")
    
    if data["nulls"]:
        print(f"\n{len(data['nulls'])} tracks from the playlist were not found on Spotify:\n")
        for track in data["nulls"]:
            print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
        print("============================================")
    
    if data["flagged"]:
        print(
            f"\nThe accuracy of {len(data['flagged'])} track(s) from the new Spotify playlist are low:\n"
        )
        for track in data["flagged"]:
            print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
        print("============================================")

    return data


def search_for_spotify_track(query, title, artists, duration, video):
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
    correct_track = None

    # Search for track on Spotify
    response = sp.search(query, type="track", limit=5)

    # Parse results to get the right track details
    for track in response["tracks"]["items"]:
        track_duration_seconds = int(track["duration_ms"] / 1000)
        track_year = int(track["album"]["release_date"][:4])
        sp_title = track["name"]
        sp_artists = [artist["name"].lower() for artist in track["artists"]]

        correct_artist = bool(
            string_similarity(artists[0], sp_artists[0]) >= 0.4 or \
            list_similarity(artists, sp_artists) >= (1 / max(len(artists), len(sp_artists))) or \
            string_similarity(str(artists), str(sp_artists)) >= 0.4
        )

        if (correct_artist and abs(track_duration_seconds - duration) <= 5) or \
        (video and correct_artist and abs(track_duration_seconds - duration) <= 90):
            flag = False

            # If string_similarity between song title from YT and Spotify is less than 0.5 OR
            # (string similarity between sole artists from YT and Spotify is less than 0.4 and
            # no similar artist in the list of artists from YT and Spotify)
            if string_similarity(title, sp_title) < 0.2 or \
            (string_similarity(artists[0], sp_artists[0]) <= 0.5 and
            list_similarity(artists, sp_artists) < (1 / max(len(artists), len(sp_artists)))):
                flag = True

            correct_track = {
                "title": sp_title,
                "artists": [artist["name"] for artist in track["artists"]],
                "year": track_year,
                "duration_seconds": track_duration_seconds,
                "uri": track["uri"],
                "flag": flag
            }
            # To prevent futher iteration after track has been found
            break

    print(f"Found {correct_track['title']} on Spotify...") if correct_track else \
    print(f"Didn't find {query} on Spotify...")
    return correct_track


# jamming of genitals
# url = "https://music.youtube.com/playlist?list=PL3Kj3Wrtj3wJl4qe3qJux6bZfnKqdmugg&feature=share"
# id = "PL3Kj3Wrtj3wJl4qe3qJux6bZfnKqdmugg"

# AlphaDev's playlist
# url2 = "https://music.youtube.com/playlist?list=PL3Kj3Wrtj3wJLW7tK-kKz-MBz6omQNFeG&feature=share"
# id2 = "PL3Kj3Wrtj3wJLW7tK-kKz-MBz6omQNFeG"
