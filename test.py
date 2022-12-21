import json
from datetime import datetime

# date = datetime.strptime("2022-03-17", '%Y-%m-%d').date()
# print(date.year)

nulls = 0

with open("spotify_playlist1.json") as file:
    content = file.read()
    content = json.loads(content)
    content = content[0:339]
    print("No. of songs:", len(content))
    for track in content:
        if not track: nulls += 1

print("Nulls:", nulls)
print("Percentage:", nulls / (len(content)) * 100, "%")
