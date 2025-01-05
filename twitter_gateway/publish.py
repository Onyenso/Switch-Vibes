"""
This file is deprecated because it has a lot of brute force code.
It will be refactored in the future. It is not currently being used.
"""

import re

import requests
from requests_oauthlib import OAuth1
import tweepy

from shared import constants as const
from spotify_to_yt.services import SpotifyToYtService
from yt_to_spotify.services import YtToSpotifyService


oauth = OAuth1(
    const.CONSUMER_KEY,
    client_secret=const.CLIENT_SECRET,
    resource_owner_key=const.ACCESS_TOKEN,
    resource_owner_secret=const.ACCESS_TOKEN_SECRET
)

tweepy_auth = tweepy.OAuth1UserHandler(
    const.CONSUMER_KEY,
    const.CLIENT_SECRET,
    const.ACCESS_TOKEN,
    const.ACCESS_TOKEN_SECRET
)

tp = tweepy.API(tweepy_auth)

def reply_mention(tweet_id, text):
    request_body = {
        'text':text,
        "reply": {"in_reply_to_tweet_id": tweet_id}
    }
    max_length = 275
    print("Publishing Tweet...")

    # Split the tweet text into chunks of max_length characters
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    num_chunks = len(chunks)
    
    # Post the first tweet in the thread
    first_chunk = chunks[0]

    first_tweet = tp.update_status(
        status=first_chunk,
        in_reply_to_status_id=request_body["reply"]["in_reply_to_tweet_id"]
    )
    
    # Post subsequent tweets in the thread
    for i in range(1, num_chunks):
        chunk = chunks[i]
        tweet = tp.update_status(
            status=chunk,
            in_reply_to_status_id=first_tweet.id_str,
            auto_populate_reply_metadata=True
        )
        # Set the ID of the first tweet in the thread to the ID of the latest tweet
        first_tweet.id_str = tweet.id_str


def save_mention_id(id):
    with open(const.ID_FILE, "w") as f:
        f.write(id)

    print("File updated with latest mention ID")
    return


# Retrieves the id from the last time the script ran
def get_mention_id():
    with open("shared/last_mention_id.txt", "r") as f:
        last_id = f.readlines()
        if not last_id:
            print("No mentions.")
            return
        last_id = last_id[len(last_id) - 1].rstrip("\n").strip()
        print("LAST MENTION ID=================================", last_id, "\n")
    return last_id


def respond_to_mentions():
    last_id = get_mention_id()
    if not last_id: return
    
    request_params = {
        "since_id": last_id,
        "expansions": "referenced_tweets.id,author_id"
    }

    # Get mentions since the last time we checked mentions
    req = requests.get(
        url=f"{const.USERS_ENDPOINT}/{const.TWITTER_USER_ID}/mentions",
        params=request_params,
        auth=oauth
    )

    res = req.json()
    print("NEW MENTIONS ==============================", res, "\n")
    length = res["meta"]["result_count"]

    if length == 0:
        print("No new mentions")
        return

    mentions: list = res["data"]
    extra_info: dict = res["includes"]

    # Reverse the order so the oldest tweets get replied to first
    for mention in reversed(mentions):
        author_id =  mention["author_id"]
        author_username = [user["username"] for user in extra_info["users"] if user["id"] == author_id][0]
        like_mention(mention, const.TWITTER_USER_ID)
        referenced_tweet = [tweet for tweet in mention["referenced_tweets"] if tweet["type"] == "replied_to"][0]
        referenced_tweet_text = [tweet["text"] for tweet in extra_info["tweets"] if tweet["id"] == referenced_tweet["id"]][0]
        mention_text = mention["text"].split("@switchthevibe")[1].strip().lower()

        # Put these in a function
        if mention_text not in ["to spotify", "to yt music"]:
            text = f"@{author_username} You have indicated a non supported conversion. " \
            "Please see my pinned tweet for usage."

        elif mention_text == "to yt music":
            tco_link = extract_tco_link(referenced_tweet_text)
            original_link = get_original_link(tco_link)
            sp_link = re.findall(const.SP_REGEX, original_link)
            print(sp_link)
            if not sp_link:
                text = f"@{author_username} A valid Spotify playlist link was not found in the tweet."
            else:
                sp_link = sp_link[0][0]
                sp_playlist_id = sp_link.split("playlist/")[1].split("?")[0]
                spotify_playlist = SpotifyToYtService.get_spotify_playlist(sp_playlist_id)
                if "404" in spotify_playlist:
                    text = f"Hey @{author_username}🙂, the requested playlist could not be found on Spotify."
                elif not spotify_playlist:
                    text = f"Hey @{author_username}😓, sorry an error occured. Please try again soon."
                else:
                    new_yt_playlist = SpotifyToYtService.convert_spotify_to_yt(spotify_playlist)
                    text = f"Hey @{author_username}🙂, here is the new YT Music playlist: {new_yt_playlist['link']}"
                    no_of_nulls = len(new_yt_playlist["nulls"])
                    no_of_flagged = len(new_yt_playlist["flagged"])
                    nulls = bool(no_of_nulls > 0)
                    flagged = bool(no_of_flagged > 0)

                    if nulls:
                        text += f"\n\nFor some reason, {no_of_nulls} track(s) from the Spotify " \
                        "playlist were not found on YT Music by our own search algorithm:\n\n"
                        for index in range(no_of_nulls):
                            text += f"{index + 1}) Title: {new_yt_playlist['nulls'][index]['title']}\nArtist: " \
                            f"{new_yt_playlist['nulls'][index]['artists']}\n"
                    else:
                        pass
                    
                    if flagged:
                        text += f"\n\nThe accuracy of {no_of_flagged} track(s) in the new YT Music playlist are low:\n\n"
                        for index in range(no_of_flagged):
                            text += f"{index + 1}) Title: {new_yt_playlist['flagged'][index]['title']}\nArtist: " \
                            f"{new_yt_playlist['flagged'][index]['artists']}\n"
                    else:
                        pass
                    text += "\nYou can now add the playlist to your library or add to a new playlist in your account."

        elif mention_text == "to spotify":
            tco_link = extract_tco_link(referenced_tweet_text)
            original_link = get_original_link(tco_link)
            yt_link = re.findall(const.YT_MUSIC_REGEX, original_link)
            print(yt_link)
            if not yt_link:
                text = f"@{author_username} A valid YT Music playlist link was not found in the tweet."
            else:
                yt_link = yt_link[0][0]
                yt_music_playlist_id = yt_link.split("?list=")[1].split("&")[0]
                yt_music_playlist = YtToSpotifyService.get_yt_playlist(yt_music_playlist_id)
                if "404" in yt_music_playlist:
                    text = f"Hey @{author_username}🙂, the requested playlist could not be found on YT Music."
                elif not yt_music_playlist:
                    text = f"Hey @{author_username}😓, sorry an error occured. Please try again soon."
                else:
                    new_spotify_playlist = YtToSpotifyService.convert_yt_to_spotify(
                        yt_music_playlist["tracks"],
                        yt_music_playlist["title"]
                    )
                    text = f"Hey @{author_username}🙂, here is the new Spotify playlist: {new_spotify_playlist['link']}"
                    no_of_nulls = len(new_spotify_playlist["nulls"])
                    no_of_flagged = len(new_spotify_playlist["flagged"])
                    nulls = bool(no_of_nulls > 0)
                    flagged = bool(no_of_flagged > 0)

                    if nulls:
                        text += f"\n\nFor some reason, {no_of_nulls} track(s) from the " \
                        "YT Music playlist were not found on Spotify by our own search algorithm:\n\n"
                        for index in range(no_of_nulls):
                            text += f"{index + 1}) Title: {new_spotify_playlist['nulls'][index]['title']}\nArtist: " \
                            f"{new_spotify_playlist['nulls'][index]['artists']}\n"
                    else:
                        pass
                    
                    if flagged:
                        text += f"\n\nThe accuracy of {no_of_flagged} track(s) in the new Spotify playlist are low:\n\n"
                        for index in range(no_of_flagged):
                            text += f"{index + 1}) Title: {new_spotify_playlist['flagged'][index]['title']}\nArtist: " \
                            f"{new_spotify_playlist['flagged'][index]['artists']}\n"
                    else:
                        pass
                    
                    text += "\nYou can now add the playlist to your library or add to a new playlist in your account."

        reply_mention(mention["id"], text)

    latest_mention_id = res["meta"]["newest_id"]
    save_mention_id(latest_mention_id)


def like_mention(tweet, user_id):
    print("Liking Tweet...")
    tweet_id = str(tweet["id"])    
    request_data = {'tweet_id': tweet_id}
    req = requests.post(url=f"{const.USERS_ENDPOINT}/{user_id}/likes", json=request_data, auth=oauth)
    print("Tweet Like Successful: ", req.json()["data"]["liked"])


def extract_tco_link(text):
    matches = re.findall(r"https?://t\.co/\w+", text)
    return matches[0] if matches else None


def get_original_link(url):
    response = requests.head(url, allow_redirects=True)
    return response.url


# TODO
# Check for multiple yt/sp links in reference tweet and ask which one should be converted
# or if all links should be converted.
# Error checking for if playlist isnt found on spotify or yt (i.e if Sp or YT returns 404).✅
# Include flagged tracks and not found tracks to tweet reply.✅
# refactor code
