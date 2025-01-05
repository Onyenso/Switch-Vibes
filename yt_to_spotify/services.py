import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

from decouple import config
from spotipy import Spotify, SpotifyOAuth
from ytmusicapi import YTMusic

from shared import constants
from shared.utils import Notifier, string_similarity, list_similarity


spotify_scope = ["playlist-modify-private", "playlist-modify-public"]

auth_manager = SpotifyOAuth(
    client_id=config("SPOTIPY_CLIENT_ID"),
    client_secret=config("SPOTIPY_CLIENT_SECRET"),
    scope=spotify_scope, redirect_uri=config("SPOTIFY_REDIRECT_URI"),
    show_dialog=True,
)

sp = Spotify(auth_manager=auth_manager)
yt = YTMusic()
shared_executor = ThreadPoolExecutor()


class YtToSpotifyService:
    @staticmethod
    def get_yt_id_from_url(url: str):
        if not url:
            return None
        
        yt_link = re.findall(constants.YT_MUSIC_REGEX, url)

        if not yt_link:
            return None
        
        yt_link = yt_link[0][0]
        yt_music_playlist_id = yt_link.split("?list=")[1].split("&")[0]
        return yt_music_playlist_id
    
    @staticmethod
    async def handle_yt_to_spotify(data, notifier=Notifier()):
        """
        Converts a YouTube Music playlist to Spotify and streams feedback via WebSocket if the request
        was made through Websocket.
        """
        try:
            url = json.loads(data).get("yt_playlist_url", None)
        except json.JSONDecodeError as e:
            await notifier.send({"detail": f"JSON parse error - {e}", "code": 400})
            return
        
        yt_playlist_id = YtToSpotifyService.get_yt_id_from_url(url)

        if not yt_playlist_id:
            await notifier.send({"detail": "Invalid YouTube Music playlist URL.", "code": 400})
            return

        try:
            playlist = yt.get_playlist(playlistId=yt_playlist_id, limit=None)
        except Exception as e:
            error_message = "Sorry, an error occurred. Please try again soon."
            if "404" in str(e):
                error_message = "The requested playlist could not be found on YT Music."
            await notifier.send({"detail": error_message, "code": 404 if "404" in str(e) else 424})
            return

        parsed_playlist = await YtToSpotifyService.parse_yt_playlist(playlist, notifier)

        spotify_playlist = await YtToSpotifyService.convert_yt_to_spotify(
            parsed_playlist["tracks"],
            parsed_playlist["title"],
            notifier
        )
        await notifier.send(spotify_playlist)
        return spotify_playlist
        
    @staticmethod
    async def parse_yt_playlist(playlist, notifier=Notifier()):
        """
        Parses the YouTube Music playlist, getting the year and duration of each track
        by searching for the track YT Music. It sends feedback for each searched track
        as the search progresses. It returns a playlist collection with the new details
        of the tracks included.
        """
        print("\n================Searching YT Music========================\n")
        await notifier.send({"message": "Searching YT Music..."})

        title = playlist["title"]
        tracks = playlist["tracks"]
        parsed_playlist_tracks = []

        # Create a ThreadPoolExecutor to handle blocking calls like yt.get_song.
        loop = asyncio.get_event_loop()

        for item in tracks:
            try:
                video_id = item["videoId"]
                year = None
                duration_seconds = item.get("duration_seconds")

                # Item is a song if videoType == MUSIC_VIDEO_TYPE_ATV or null.
                video = False if item["videoType"] == "MUSIC_VIDEO_TYPE_ATV" or not item["videoType"] else True
                
                # Some tracks have null videoID
                if video_id:
                    # Run the blocking `yt.get_song` call in a thread pool.
                    music_data = await loop.run_in_executor(shared_executor, yt.get_song, video_id)

                    # Parse the release date
                    published_date = music_data["microformat"]["microformatDataRenderer"]["publishDate"]
                    published_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%S%z').date()
                    year = published_date.year
                    duration_seconds = music_data["videoDetails"]["lengthSeconds"]

                track_info = {
                    "title": item["title"],
                    "artists": [artist["name"] for artist in item["artists"]],
                    "year": year,
                    "duration_seconds": int(duration_seconds) if duration_seconds else 0,
                    "video": video
                }

                parsed_playlist_tracks.append(track_info)

                message = f"Found {item['title']} on YT Music..."
                print(message)
                await notifier.send({"message": message, "track": track_info})

            except Exception as e:
                await notifier.send({"message": f"Error processing track {item['title']}: {str(e)}"})

        print("\n================YT Music Done========================\n")
        await notifier.send({"message": "YT Music Done"})
        return {"tracks": parsed_playlist_tracks, "title": title}
    
    @staticmethod
    async def convert_yt_to_spotify(playlist_tracks, playlist_title, notifier=Notifier()):
        """
        This method converts a YT Music playlist to Spotify. It searches for each track
        from the YT Music playlist, on Spotify, creates a new playlist on Spotify and adds the found
        tracks to the new playlist.
        """
        print("\n================Searching Spotify========================\n")
        await notifier.send({"message": "Searching Spotify..."})

        parsed_spotify_playlist = []
        nulls = []

        for track in playlist_tracks:
            # E.g. Miss You Bad Mr Eazi Burna Boy
            q = f"{track['title']} {' '.join(track['artists'])}".strip()

            sp_track = await YtToSpotifyService.search_for_spotify_track(
                query=q,
                title=track["title"],
                artists=[artist.lower() for artist in track["artists"]],
                duration=int(track["duration_seconds"]),
                video=track["video"],
                notifier=notifier
            )

            if sp_track:
                parsed_spotify_playlist.append(sp_track)
            else:
                nulls.append({"title": track["title"], "artists": track["artists"]})
        
        print("\n================Spotify Done========================\n")
        await notifier.send({"message": "Spotify Done"})

        # Create playlist.
        spotify_playlist = sp.user_playlist_create(
            user=config("SPOTIFY_ID"),
            name=playlist_title,
            public=False,
            description="Generated by SwitchVibes."
        )
        
        # Get uris of tracks from parsed playlist.
        uris =[track["uri"] for track in parsed_spotify_playlist]
        
        # Add tracks to the created Spotify playlist.
        for start in range(0, len(uris), 100):
            sp.playlist_add_items(playlist_id=spotify_playlist["id"], items=uris[start:start + 100])

        data = {
            "link": spotify_playlist["external_urls"]["spotify"],
            "playlist": parsed_spotify_playlist,
            "nulls": nulls,
            "flagged": [
                {"title": track["title"], "artists": track["artists"]} for \
                track in parsed_spotify_playlist if track["flag"]
            ]
        }

        print(f"Spotify Playlist: {data['link']}\n")
        
        if data["nulls"]:
            print(f"\n{len(data['nulls'])} track(s) from the playlist were not found on Spotify:\n")

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
    
    @staticmethod
    async def search_for_spotify_track(query, title, artists, duration, video, notifier=Notifier()):
        """
        Searches for a track YT Music track on Spotify using title, artist and duration of track
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
        loop = asyncio.get_event_loop()

        # Search for track on Spotify
        await asyncio.sleep(0.01)
        try:
            search_func = partial(sp.search, q=query, type="track", limit=5)

            # Run the blocking sp.search call in the thread pool.
            response = await loop.run_in_executor(shared_executor, search_func)

            # Parse results to get the right track details.
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

                if (
                    correct_artist and abs(track_duration_seconds - duration) <= 5
                ) or (
                    video and correct_artist and abs(track_duration_seconds - duration) <= 90
                ):
                    flag = False

                    # If string_similarity between song title from YT and Spotify is less than 0.2 OR
                    # (string similarity between sole artists from YT and Spotify is less than 0.5 and
                    # no similar artist in the list of artists from YT and Spotify):
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
                    # To prevent further iteration after track has been found
                    break
        except Exception as e:
            await notifier.send({"message": f"Error searching for {query} on Spotify: {str(e)}"})
            return None
        
        if correct_track:
            message = f"Found {correct_track['title']} on Spotify..."
        else:
            message = f"Didn't find {query} on Spotify..."
            
        print(message)
        await notifier.send({"message": message, "track": correct_track})
        return correct_track
