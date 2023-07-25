import threading

from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.decorators import APIView
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from switch_vibes.publish import respond_to_mentions
from switch_vibes.spotify_to_yt import get_spotify_playlist, convert_spotify_to_yt, get_spotify_id_from_url
from switch_vibes.yt_to_spotify import get_yt_playlist, convert_yt_to_spotify, get_yt_id_from_url, search_for_spotify_track, sp


def index(request):
    # respond_to_mentions()
    return HttpResponse("Hello World! Welcome to Switch Vibes! The server is running.")


class YtToSpotify(APIView):
    def post(self, request, format=None):
        yt_playlist_url = request.data.get("yt_playlist_url")

        if not yt_playlist_url:
            return Response({"error": "yt_playlist_url is required."}, status=400)
        
        yt_id = get_yt_id_from_url(yt_playlist_url)

        if not yt_id:
            return Response({"error": "Invalid YouTube playlist URL."}, status=400)
        
        yt_playist = get_yt_playlist(yt_id)

        if not yt_playist:
            return Response({"error": "Sorry an error occured. Please try again soon."}, status=500)

        if "404" in yt_playist:
            return Response({"error": "The requested playlist could not be found on YT Music."}, status=404)
        
        new_spotify_playlist = convert_yt_to_spotify(yt_playist["tracks"], yt_playist["title"])
        return Response(new_spotify_playlist, status=200)


class SpotifyToYt(APIView):
    def post(self, request, format=None):
        spotify_playlist_url = request.data.get("spotify_playlist_url")

        if not spotify_playlist_url:
            return Response({"error": "spotify_playlist_url is required."}, status=400)
        
        spotify_id = get_spotify_id_from_url(spotify_playlist_url)

        if not spotify_id:
            return Response({"error": "Invalid Spotify playlist URL."}, status=400)
        
        spotify_playist = get_spotify_playlist(spotify_id)

        if not spotify_playist:
            return Response({"error": "Sorry an error occured. Please try again soon."}, status=500)

        if "404" in spotify_playist:
            return Response({"error": "The requested playlist could not be found on Spotify."}, status=404)
        
        new_yt_playlist = convert_spotify_to_yt(spotify_playist)
        return Response(new_yt_playlist, status=200)


# class YtToSpotify2(APIView):
#     def post(self, request, format=None):
#         yt_playlist_url = request.data.get("yt_playlist_url")

#         if not yt_playlist_url:
#             return Response({"error": "yt_playlist_url is required."}, status=400)
        
#         yt_id = get_yt_id_from_url(yt_playlist_url)

#         if not yt_id:
#             return Response({"error": "Invalid YouTube playlist URL."}, status=400)
        
#         yt_playist = get_yt_playlist(yt_id)

#         if not yt_playist:
#             return Response({"error": "Sorry an error occured. Please try again soon."}, status=500)

#         if "404" in yt_playist:
#             return Response({"error": "The requested playlist could not be found on YT Music."}, status=404)
        
#         parsed_spotify_playlist = []
#         nulls = []

#         def generate_response():

#             print("\n================Searching Spotify========================\n")

#             for track in yt_playist["tracks"]:
#                 found = False
#                 artists = ""

#                 for artist in track["artists"]:
#                     artists += artist + " "

#                 artists = artists.strip()

#                 # E.g. Miss You Bad Mr Eazi Burna Boy
#                 q = f"{track['title']} {artists}"

#                 sp_track = search_for_spotify_track(
#                     query=q,
#                     title=track["title"],
#                     artists=[artist.lower() for artist in track["artists"]],
#                     duration=int(track["duration_seconds"]),
#                     video=track["video"]
#                 )

#                 # If track is found, add to parsed playlist else add track to nulls
#                 if sp_track:
#                     found = True
#                     parsed_spotify_playlist.append(sp_track)
#                 else:
#                     nulls.append({
#                     "title": track["title"],
#                     "artists": track["artists"]
#                 })
            
#                 yield {"track": track, "found": found}
            
#             print("\n================Spotify Done========================\n")
        
#         iterator = generate_response()
#         for item in iterator: ...
        
#         # Create playlist
#         spotify_playlist = sp.user_playlist_create(
#             user=config("SPOTIFY_ID"),
#             name=yt_playist["title"],
#             public=False,
#             description="Generated by Switch Vibes."
#         )

#         # Get uris of tracks from parsed playlist
#         uris =[track["uri"] for track in parsed_spotify_playlist]
#         start = 0
#         stop = 100
        
#         # Add tracks to the created Spotify playlist
#         while True:
#             sp.playlist_add_items(
#                 playlist_id=spotify_playlist["id"],
#                 items=uris[start:stop]
#             )
#             if stop > len(uris): break
#             start = stop
#             stop += 100

#         data = {
#             "link": spotify_playlist["external_urls"]["spotify"],
#             "spotify_playlist": parsed_spotify_playlist,
#             "nulls": nulls,
#             "flagged": [
#                 {"title": track["title"], "artists": track["artists"]} for \
#                 track in parsed_spotify_playlist if track["flag"]
#             ]
#         }

#         print(f"Spotify Playlist: {data['link']}\n")
    
#         if data["nulls"]:
#             print(f"\n{len(data['nulls'])} tracks from the playlist were not found on Spotify:\n")
#             for track in data["nulls"]:
#                 print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
#             print("============================================")
        
#         if data["flagged"]:
#             print(f"\nThe accuracy of {len(data['flagged'])} track(s) from the new Spotify playlist are low:\n")
#             for track in data["flagged"]:
#                 print(f"Title: {track['title']}\nArtist: {track['artists']}\n")
#             print("============================================")
        
#         response = StreamingHttpResponse(streaming_content=iterator, content_type="application/json")
#         response["Content-Disposition"] = 'attachment; filename="response.json"'
#         # return Response(new_spotify_playlist, status=200)
#         return response


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=respond_to_mentions, trigger="interval", seconds=3)
# scheduler.start()
# atexit.register(lambda: scheduler.shutdown())
