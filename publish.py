import os
import sys
import time
import json
import requests
import constants as const
from requests_oauthlib import OAuth1, OAuth2


oauth = OAuth1(
    const.CONSUMER_KEY,
    client_secret=const.CLIENT_SECRET,
    resource_owner_key=const.ACCESS_TOKEN,
    resource_owner_secret=const.ACCESS_TOKEN_SECRET
)


def reply_mention(tweet_id, text):
    request_body = {
        'text':text,
        "reply": {"in_reply_to_tweet_id": tweet_id}
    }

    print("Publishing Tweet...")

    req = requests.post(url=const.POST_TWEET_ENDPOINT_2, json=request_body, auth=oauth)
    print("Tweet Published") if req.status_code == "200" else print("Tweet Not Published.")
    print("Status code:", req.status_code)


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
        print("LAST MENTION ID=================================", last_id, "\n")
    return last_id


def respond_to_mentions():
    last_id = get_mention_id()
    if not last_id: return
    
    # Get mentions since the last time we checked mentions
    req = requests.get(
        url=f"{const.USERS_ENDPOINT}/{const.TWITTER_USER_ID}/mentions?since_id={last_id}&expansions=referenced_tweets.id,author_id",
        auth=oauth
    )

    res = req.json()
    print("NEW MENTIONS ==============================", res, "\n")
    length = res["meta"]["result_count"]

    if length == 0:
        print("No new mentions")
        return

    mentions = res["data"]
    extra_info = res["includes"]

    # Reverse the order so the oldest tweets get replied to first
    for mention in reversed(mentions):
        author_id =  mention["author_id"]
        author_username = [user["username"] for user in extra_info["users"] if user["id"] == author_id][0]
        like_mention(mention, const.TWITTER_USER_ID)

        referenced_tweet = [tweet for tweet in mention["referenced_tweets"] if tweet["type"] == "replied_to"][0]

        referenced_tweet_text = [tweet["text"] for tweet in extra_info["tweets"] if tweet["id"] == referenced_tweet["id"]][0]

        # parse the text from the referenced tweet to get the link
        # return an error if no link is found
        # get the text of the mention to know what to convert

        text = f"@{author_username} This has to work!"
        reply_mention(mention["id"], text)

    latest_mention_id = res["meta"]["newest_id"]
    save_mention_id(latest_mention_id)


def like_mention(tweet, user_id):
    print("Liking Tweet...")
    tweet_id = str(tweet["id"])    
    request_data = {'tweet_id': tweet_id}
    req = requests.post(url=f"{const.USERS_ENDPOINT}/{user_id}/likes", json=request_data, auth=oauth)
    print("Tweet Like Successful: ", req.json()["data"]["liked"])


respond_to_mentions()

# TODO
# Switch api calls to Twitter V2

