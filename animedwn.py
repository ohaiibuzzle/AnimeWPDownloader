#!/usr/bin/env python3

import os
import requests
import re
import sys

# Change these to your liking. Should work fine for everything.

reddit_loc = "https://www.reddit.com/r/Animewallpaper/new.json"
down_dir = "Anime Wallpapers/"

allow_nsfw = False
also_mobile = False
try_emoji = False
only_mobile = False

if sys.argv.__contains__("--allow-nsfw"):
    allow_nsfw = True
if sys.argv.__contains__("--also-mobile"):
    also_mobile = True
if sys.argv.__contains__("--try-emoji"):
    try_emoji = True
if sys.argv.__contains__("--only-mobile"):
    only_mobile = True

if sys.argv.__contains__("--help"):
    print("Possible Arguments:")
    print("         --allow-nsfw: Allow NSFW WP downloads")
    print("         --also-mobile: Allow mobile WP downloads")
    print("         --only-mobile: Only allow mobile WP downloads")
    print("         --try-emoji: Try to save files with emoji in the name")
    print("                      (Explodes badly in Windows)")
    exit(0)

def emoji_be_gone(inputString: str):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U0001F1F2-\U0001F1F4"  # Macau flag
                               u"\U0001F1E6-\U0001F1FF"  # flags
                               u"\U0001F600-\U0001F64F"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U0001F1F2"
                               u"\U0001F1F4"
                               u"\U0001F620"
                               u"\u200d"
                               u"\u2640-\u2642"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', inputString)


request_header = {
    'User-Agent': 'Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
}

if os.path.exists(down_dir):
    os.chdir(down_dir)
else:
    os.mkdir(down_dir)
    os.chdir(down_dir)

existing_files = os.listdir()

anime_new = requests.get(reddit_loc, headers=request_header).json()
post_list = anime_new.get('data').get('children')

for _ in post_list:

    img_json = _.get('data')
    if not try_emoji:
        img_title = emoji_be_gone(img_json.get('title').replace('/', " ").replace(':', " ").replace("\"", "\'"))
    else:
        img_title = img_json.get('title')
    img_link = img_json.get('url')

    if img_json.get('over_18') and not allow_nsfw:
        print(img_title + " is marked with NSFW. Not downloading.")
        continue

    if (img_json.get('link_flair_text') == 'Mobile' and not also_mobile) and not only_mobile:
        print(img_title + " is for mobile. Not downloading.")
        continue

    elif img_title + ".png" in existing_files:
        print(img_title + " already exists.")
        continue

    elif only_mobile:
        if img_json.get('link_flair_text') != 'Mobile':
            print(img_title + " isn't for mobile. Not downloading.")
            continue
        else:
            try:
                with open(img_title + ".png", 'wb') as handle:
                    img = requests.get(img_link).content
                    handle.write(img)
                    print(img_title + ".png" + " successfully downloaded")
            except OSError:
                print('Can\'t save ' + img_title + '. Weird')

    else:
        try:
            with open(img_title + ".png", 'wb') as handle:
                img = requests.get(img_link).content
                handle.write(img)
                print(img_title + ".png" + " successfully downloaded")
        except OSError:
            print('Can\'t save ' + img_title + '. Weird')