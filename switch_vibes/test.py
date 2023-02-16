import json
from datetime import datetime
import requests


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

import re

def extract_tco_link(text):
    # Define the regular expression pattern to match a t.co link
    pattern = r"https?://t\.co/\w+"
    # Use the re.findall function to search for all matches in the text
    matches = re.findall(pattern, text)
    # Return the first match if any matches were found, otherwise return None
    return matches[0] if matches else None

def get_original_link(short_link):
    response = requests.get(short_link, allow_redirects=True)
    if response.status_code == 200:
        if "Location" in response.headers:
            return response.headers["Location"]
        return response.headers
    print("Error: Response returned status code", response.status_code)
    print("Error message:", response.text)
    return None


def get_final_url(url):
    response = requests.head(url, allow_redirects=True)
    return response.url




# Example usage:
text = "This is a test tweet to test a bot.\n\nHere is my playlist: https://t.co/SpmqVz6nJj\n\nYou'll love it."
tco_link = extract_tco_link(text)
# original_link = get_original_link(tco_link)
final_url = get_final_url(tco_link)

print("Final URL:", final_url)
print("The t.co link is:", tco_link)
# print((original_link))
