import os
import sys
import time
import json
import requests
import constants as const
from requests_oauthlib import OAuth1, OAuth1Session


oauth = OAuth1(
    const.CONSUMER_KEY,
    client_secret=const.CLIENT_SECRET,
    resource_owner_key=const.ACCESS_TOKEN,
    resource_owner_secret=const.ACCESS_TOKEN_SECRET
)


def reply_tweet(tweet_id, text):
    request_data = {'status':text, "in_reply_to_status_id": tweet_id}
    print("Publishing Tweet...")
    req = requests.post(url=const.POST_TWEET_ENDPOINT, data=request_data, auth=oauth)
    print("Tweet Published") if req.status_code == "200" else print("Tweet Not Published.")
    print("Status code:", req.status_code)


def get_my_id():
    req = requests.get(url=f"{const.USERS_ENDPOINT}/by/username/{const.TWITTER_USERNAME}", auth=oauth)
    req = req.json()
    user_id = req["data"]["id"]


def save_mention_id(id):
    with open(const.ID_FILE, "w") as f:
        f.write(id)

    print("File updated with latest mention ID")
    return


# Retrieves the id from the last time the script ran
def get_mention_id():
    with open(const.ID_FILE, "r") as f:
        last_id = f.readlines()
        if not last_id:
            print("No mentions.")
            return
        last_id = last_id[len(last_id) - 1].rstrip("\n").strip()
        print("LAST MENTION ID=================================", last_id)
    return last_id


def respond_to_mentions(my_user_id):
    last_id = get_mention_id()
    if not last_id: return
    
    # Get mentions since the last time we checked mentions
    req = requests.get(
        url=f"{const.USERS_ENDPOINT}/{my_user_id}/mentions?since_id={last_id}&expansions=author_id",
        auth=oauth
    )

    res = req.json()
    print(res)
    length = res["meta"]["result_count"]

    if length == 0:
        print("No new mentions")
        return

    mentions = res["data"]

    # Reverse the order so the oldest tweets get replied to first
    for mention in reversed(mentions):
        author_id =  mention["author_id"]
        mention_username = get_username(author_id)
        like_tweet(mention, my_user_id)
        text = f"@{mention_username} This has to work!"
        reply_tweet(mention["id"], text)

    latest_mention_id = res["meta"]["newest_id"]
    save_mention_id(latest_mention_id)


def get_username(id):
    req = requests.get(url=f"{const.USERS_ENDPOINT}/{id}", auth=oauth)
    res = req.json()
    username = res["data"]["username"]
    return username


def like_tweet(tweet, user_id):
    print("Liking Tweet...")
    tweet_id = str(tweet["id"])    
    request_data = {'tweet_id': tweet_id}
    req = requests.post(url=f"{const.USERS_ENDPOINT}/{user_id}/likes", json=request_data, auth=oauth)
    print("Tweet Like Successful: ", req.json()["data"]["liked"])


respond_to_mentions("1483837126269616135")
