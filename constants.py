import os

ID_FILE = "last_mention_id.txt"

TWITTER_USERNAME = "switchthevibe"
POST_TWEET_ENDPOINT = 'https://api.twitter.com/1.1/statuses/update.json'
USERS_ENDPOINT = "https://api.twitter.com/2/users"

# Twitter API vars
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CLIENT_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

AWS_ACCESS_KEY = "AKIARVBZH7MLYHY6YDM3"
AWS_SECRET_ACCESS_KEY="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"
