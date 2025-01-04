import os
from dotenv import load_dotenv


load_dotenv()

ID_FILE = "shared/last_mention_id.txt"

TWITTER_USERNAME = "switchthevibe"
POST_TWEET_ENDPOINT = 'https://api.twitter.com/1.1/statuses/update.json'
POST_TWEET_ENDPOINT_2 = "https://api.twitter.com/2/tweets"
GET_TWEET_ENDPOINT = "https://api.twitter.com/1.1/statuses/show.json"
USERS_ENDPOINT = "https://api.twitter.com/2/users"
TWITTER_USER_ID = "1483837126269616135"
SP_REGEX = "(?P<link>(https?://)?open\.spotify\.com/playlist/[a-zA-Z0-9]+)"
YT_MUSIC_REGEX = "(?P<link>(https?://)?music\.youtube\.com/playlist\?list=[a-zA-Z0-9-_]+)"

# Twitter API vars
CONSUMER_KEY = os.environ.get("TWITTER_API_KEY")
CLIENT_SECRET = os.environ.get("TWITTER_API_KEY_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
