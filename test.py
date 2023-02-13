import json
from datetime import datetime

# date = datetime.strptime("2022-03-17", '%Y-%m-%d').date()
# print(date.year)

nulls = 0

# with open("spotify_playlist4.json") as file:
#     content = file.read()
#     content = json.loads(content)
#     for track in content:
#         if not track: nulls += 1


# print("\nFILE:", file.name)
# print("NO. OF SONGS:", len(content))
# print("NULLS:", nulls)
# print("PERCENTAGE OF NULS:", nulls / (len(content)) * 100, "%\n")

extra_info = includes = {
    "users": [
        {
            "id": "1224394342774792192",
            "name": "AlphaDev",
            "username": "YensoUchenna"
        },
        {
            "id": "1618651917155975183",
            "name": "Switch Vibes",
            "username": "switchthevibes"
        }
    ],
    "tweets": [
        {
            "edit_history_tweet_ids": [
                "1624873817641295874"
            ],
            "text": "Testing API",
            "author_id": "1483837126269616135",
            "id": "1624873817641295874"
        }
    ]
}

alpha = [user["username"] for user in extra_info["users"] if user["id"] == "1618651917155975183"]
print(alpha)