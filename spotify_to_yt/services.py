import asyncio
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from spotipy import Spotify, SpotifyOAuth
from ytmusicapi import YTMusic

from shared import constants
from shared.utils import Notifier, string_similarity, list_similarity


spotify_scope = ["playlist-modify-private", "playlist-modify-public"]

auth_manager = SpotifyOAuth(
    client_id=settings.SPOTIPY_CLIENT_ID,
    client_secret=settings.SPOTIPY_CLIENT_SECRET,
    scope=spotify_scope,
    redirect_uri=settings.SPOTIFY_REDIRECT_URI,
    show_dialog=True,
)

sp = Spotify(auth_manager=auth_manager)
yt = YTMusic(auth="yt_to_spotify/headers_auth3.json")

shared_executor = ThreadPoolExecutor()


class SpotifyToYtService:
    @staticmethod
    def get_spotify_id_from_url(url: str) -> str | None:
        """
        Extracts the id of a Spotify playlist from its url.
        """
        if not url:
            return None
        
        sp_link = re.findall(constants.SP_REGEX, url)

        if not sp_link:
            return None
        
        sp_link = sp_link[0][0]
        sp_playlist_id = sp_link.split("playlist/")[1].split("?")[0]
        return sp_playlist_id
    
    @staticmethod
    async def handle_spotify_to_yt(data, notifier=Notifier()):
        """
        Converts a Spotify playlist to YT Music and streams feedback via WebSocket if the request
        was made through Websocket.
        """
        try:
            url = json.loads(data).get("spotify_playlist_url", None)
        except json.JSONDecodeError as e:
            await notifier.send({"detail": f"JSON parse error - {e}", "code": 400})
            return
        
        spotify_playlist_id = SpotifyToYtService.get_spotify_id_from_url(url)

        if not spotify_playlist_id:
            await notifier.send({"detail": "Invalid Spotify playlist URL.", "code": 400})
            return
        
        parsed_playlist = await SpotifyToYtService.parse_spotify_playlist(spotify_playlist_id, notifier)
        yt_music_playlist = await SpotifyToYtService.convert_spotify_to_yt(parsed_playlist, notifier)
        if yt_music_playlist:
            await notifier.send(yt_music_playlist)
        return yt_music_playlist
    
    @staticmethod
    async def parse_spotify_playlist(playlist_id: str, notifier=Notifier()):
        """
        Gets a Spotify playlist from its id and returns a collection that includes
        the tracks of the playlist.
        """
        # Get the first 100 tracks from playlist
        try:
            parsed_playlist_tracks: Any = sp.playlist(
                playlist_id=playlist_id,
                fields="id,name,tracks.items(track(name,duration_ms,artists(name))),tracks.next",
            )
        except Exception as e:
            error_message = "Sorry an error occurred. Please try again soon."
            if "404" in str(e):
                error_message = "The requested playlist could not be found on Spotify."
            await notifier.send({"detail": error_message, "code": 404 if "404" in str(e) else 424})
            return
        
        print("\n================Searching Spotify========================\n")
        await notifier.send({"message": "Searching Spotify..."})

        next = parsed_playlist_tracks["tracks"]["next"]
        offset = 0

        # Get the remaining tracks, 100 at a time, if there's more.
        while next is not None:
            offset += 100

            next_tracks: Any = sp.playlist_items(
                playlist_id=playlist_id,
                fields="items(track(name,artists(name),duration_ms)),next",
                offset=offset
            )

            parsed_playlist_tracks["tracks"]["items"].extend(next_tracks["items"])
            next = next_tracks["next"]
            parsed_playlist_tracks["tracks"]["next"] = next

        print("\n================Spotify Done========================\n")
        await notifier.send({"message": "Spotify Done"})
        return parsed_playlist_tracks
    
    @staticmethod
    async def get_youtube_access_token():
        """
        Loads oauth.json, refreshes if expired, then returns a valid access token.
        """
        oauth_file = Path("yt_to_spotify/oauth.json")
        creds = json.loads(oauth_file.read_text())

        # Check if token is expired or about to expire
        if creds.get("expires_at", 0) - time.time() < 60:
            data = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": creds["refresh_token"],
            }

            response = requests.post("https://oauth2.googleapis.com/token", data=data)
            response.raise_for_status()

            new = response.json()
            creds["access_token"] = new["access_token"]
            creds["expires_in"] = new["expires_in"]
            creds["expires_at"] = int(time.time()) + new["expires_in"]

            # Google may return a new refresh_token
            if "refresh_token" in new:
                creds["refresh_token"] = new["refresh_token"]
            
            oauth_file.write_text(json.dumps(creds))
        
        return creds["access_token"]

    @staticmethod
    async def create_youtube_playlist(access_token: str, title: str, description: str, privacy_status: str, video_ids: list):
        """
        Creates a YouTube Music playlist using the YouTube Data API v3.
        Returns the playlist ID.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Step 1: Create the playlist
        create_url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet,status"
        playlist_data = {
            "snippet": {
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy_status.lower(),  # API expects lowercase
            }
        }

        response = requests.post(create_url, headers=headers, json=playlist_data)
        response.raise_for_status()
        playlist_id = response.json()["id"]

        # Step 2: Add videos to the playlist
        insert_url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
        for video_id in video_ids:
            item_data = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id,
                    }
                }
            }
            try:
                resp = requests.post(insert_url, headers=headers, json=item_data)
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                # Skip videos that can't be added (e.g., unavailable)
                continue

        return playlist_id
    
    @staticmethod
    async def convert_spotify_to_yt(spotify_playlist: dict, notifier=Notifier()):
        """
        This method converts a Spotify playlist to YT Music. It searches for each track
        from the Spotify playlist, on YT Music, creates a new playlist on YT Music and adds the found
        tracks to the new playlist.
        """
        if not spotify_playlist:
            return
        
        print("\n================Searching YT Music========================\n")
        await notifier.send({"message": "Searching YT Music..."})

        parsed_yt_playlist = []
        nulls = []
        sp_playlist_name = spotify_playlist["name"]
        sp_tracks = spotify_playlist["tracks"]["items"]

        for sp_track in sp_tracks:
            sp_artists = ""

            for sp_artist in sp_track["track"]["artists"]:
                sp_artists += sp_artist["name"] + " "
                
            sp_artists = sp_artists.strip()
            q = f"{sp_track['track']['name']} {sp_artists}"

            yt_track = await SpotifyToYtService.search_for_yt_track(
                query=q,
                title=sp_track["track"]["name"],
                artists=[artist['name'].lower() for artist in sp_track["track"]["artists"]],
                duration=int(sp_track["track"]["duration_ms"] / 1000),
                index=sp_tracks.index(sp_track),
                notifier=notifier
            )
        
            if yt_track:
                parsed_yt_playlist.append(yt_track)
            else:
                nulls.append({"title": sp_track['track']["name"], "artists": sp_track['track']["artists"]})

        print("\n================YT Music Done========================\n")
        await notifier.send({"message": "YT Music Done"})

        # Get access token and create playlist using YouTube Data API v3
        access_token = await SpotifyToYtService.get_youtube_access_token()

        # Create yt playlist and add tracks.
        yt_playlist = await SpotifyToYtService.create_youtube_playlist(
            access_token=access_token,
            title=sp_playlist_name,
            description="Generated by Switch Vibes.",
            privacy_status="unlisted",
            video_ids=[track["yt_id"] for track in parsed_yt_playlist]
        )

        data = {
            "link": f"https://music.youtube.com/playlist?list={yt_playlist}",
            "playlist": parsed_yt_playlist,
            "nulls": nulls,
            "flagged": [
                {
                    "title": track["title"],
                    "artists": track["artists"]
                } for track in parsed_yt_playlist if track["flag"]
            ]
        }

        print(f"YT Music Playlist: {data['link']}\n")

        if data["nulls"]:
            print(f"\n{len(data['nulls'])} tracks from the playlist were not found on YT Music:\n")

            for track in data["nulls"]:
                print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
            print("============================================")
        
        if data["flagged"]:
            print(f"\nThe accuracy of {len(data['flagged'])} track(s) from the new YT Music playlist are low:\n")

            for track in data["flagged"]:
                print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
            print("============================================")

        return data
    
    @staticmethod
    async def search_for_yt_track(query, title, artists, duration, index, notifier=Notifier()):
        """This method searches for a Spotify track on YT Music."""
        correct_track = None
        loop = asyncio.get_event_loop()

        try:
            search_func = partial(yt.search, query=query, filter="songs", limit=5)
            response = await loop.run_in_executor(shared_executor, search_func)

            for yt_track in response:
                yt_track_duration = yt_track["duration_seconds"]
                yt_track_title = yt_track["title"]
                yt_track_artists = [artist["name"].lower() for artist in yt_track["artists"]]
                yt_track_id = yt_track["videoId"]

                correct_artist = bool(
                    (
                        yt_track_artists and artists and string_similarity(yt_track_artists[0], artists[0]) >= 0.4
                    ) or
                    (
                        yt_track_artists and list_similarity(yt_track_artists, artists) >= \
                        (1 / max(len(yt_track_artists), len(artists)))
                    ) or
                    string_similarity(str(yt_track_artists), str(artists)) >= 0.4
                )

                if (correct_artist and abs(yt_track_duration - duration) <= 5):
                    flag = False

                    # If string_similarity between song title from YT and Spotify is less than 0.2 OR
                    # (string similarity between sole artists from YT and Spotify is less than 0.5 and
                    # no similar artist in the list of artists from YT and Spotify)
                    if string_similarity(yt_track_title, title) < 0.2 or \
                    (
                        string_similarity(yt_track_artists[0], artists[0]) <= 0.5 and
                        list_similarity(yt_track_artists, artists) < (1 / max(len(yt_track_artists), len(artists)))
                    ):
                        flag = True
                    
                    correct_track = {
                        "title": yt_track_title,
                        "artists": [artist["name"] for artist in yt_track["artists"]],
                        "duration_seconds": yt_track_duration,
                        "yt_id": yt_track_id,
                        "yt_url": f"https://music.youtube.com/watch?v={yt_track_id}",
                        "flag": flag
                    }
                    break
        except Exception as e:
            await notifier.send({"message": f"Error searching for {query} on Spotify: {str(e)}"})
            return None
        
        if correct_track:
            message = f"{index + 1}) Found {correct_track['title']} on YT Music..."
        else:
            message = f"{index + 1}) Didn't find {query} on YT Music..."

        print(message)
        await notifier.send({"message": message, "track": correct_track})
        return correct_track
