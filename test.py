import json
from datetime import datetime

# date = datetime.strptime("2022-03-17", '%Y-%m-%d').date()
# print(date.year)

nulls = 0

# with open("spotify_playlist1.json") as file:
#     content = file.read()
#     content = json.loads(content)
#     print("No. of songs:", len(content))
#     for track in content:
#         if not track: nulls += 1

# print("Nulls:", nulls)
# print("Percentage:", nulls / (len(content)) * 100, "%")

with open("raw_yt_playlist.json") as file:
    playlist = json.loads(file.read())

# tracks with artists greater than 1
for track in playlist["tracks"]:
    if len(track["artists"]) > 1:
        print(f"{playlist['tracks'].index(track)}")
