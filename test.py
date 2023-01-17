import json
from datetime import datetime

# date = datetime.strptime("2022-03-17", '%Y-%m-%d').date()
# print(date.year)

nulls = 0

with open("spotify_playlist3.json") as file:
    content = file.read()
    content = json.loads(content)
    for track in content:
        if not track: nulls += 1


print("\nFILE:", file.name)
print("NO. OF SONGS:", len(content))
print("NULLS:", nulls)
print("PERCENTAGE OF NULS:", nulls / (len(content)) * 100, "%\n")
