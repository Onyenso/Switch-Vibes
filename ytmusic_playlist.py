from datetime import datetime
from ytmusicapi import YTMusic
import json
from spotify_music import convert_yt_to_spotify


"""
Things to check for YT to Spotify and vice versa:
# track title.lower
# duration_difference ! >= 10 secs
# artist name
# year
"""

yt = YTMusic()


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

    playlist = yt.get_playlist(playlistId=playlist_id, limit=None)
    tracks = playlist["tracks"]
    parsed_playlist_tracks = []

    for item in tracks:
        # Get ID of track
        videoID = item["videoId"]
        year = None
        duration_seconds = item["duration_seconds"]
        
        # Item is a song if videoType == MUSIC_VIDEO_TYPE_ATV or null
        video = False if item["videoType"] == "MUSIC_VIDEO_TYPE_ATV" or not item["videoType"] else True

        # Some tracks have null videoID
        if videoID:
            # Get track data
            music_data = yt.get_song(videoId=videoID)

            # Get release date of track from track data
            published_date = music_data["microformat"]["microformatDataRenderer"]["publishDate"]
            published_date = datetime.strptime(published_date, '%Y-%m-%d').date()
            year = published_date.year

            # duration gotten from playlist does not match sometimes
            duration_seconds = music_data["videoDetails"]["lengthSeconds"]

        parsed_playlist_tracks.append({
            "title": item["title"],
            "artists": [artists["name"] for artists in item["artists"]],
            "year": year,
            "duration_seconds": duration_seconds,
            "video": video
        })

        print(f"Adding {item['title']}...")

    print("================YT Music Done========================")
    return parsed_playlist_tracks


# jamming of genitals
id = "PL3Kj3Wrtj3wJl4qe3qJux6bZfnKqdmugg"
# url = "https://music.youtube.com/playlist?list=PL3Kj3Wrtj3wJl4qe3qJux6bZfnKqdmugg&feature=share"

# AlphaDev's playlist
id2 = "PL3Kj3Wrtj3wJLW7tK-kKz-MBz6omQNFeG"
# url2 = "https://music.youtube.com/playlist?list=PL3Kj3Wrtj3wJLW7tK-kKz-MBz6omQNFeG&feature=share"

# get YT playlist
# raw_yt_playlist = yt.get_playlist(id2, limit=None)
# yt_playlist = get_yt_playlist(id2)

# write parsed YT playlist to file
# with open("yt_playlist2.json", "w") as file:
#     json.dump(yt_playlist, file, indent=4)

# get parsed YT playlist from a file
# with open("yt_playlist1.json") as file:
#     yt_playlist = json.loads(file.read())

# convert parsed YT playlist to Spotify playlist and write to a file
# with open("spotify_playlist2.json", "w") as file:
#     json.dump(convert_yt_to_spotify(yt_playlist), file, indent=4)

print(json.dumps(yt.get_song(videoId="FKkfCUZdU3s"), indent=4))
print("Done.")
