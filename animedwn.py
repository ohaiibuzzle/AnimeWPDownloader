import os
import requests
import re

# Change these to your liking. Should work fine for everything.

reddit_loc = "https://www.reddit.com/r/Animewallpaper/new.json"
down_dir = "Anime Wallpapers/"
allow_nsfw = False
also_mobile = True

def emoji_be_gone(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')


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
    img_title = emoji_be_gone(img_json.get('title').replace("\"", ""))

    if img_json.get('over_18') and not allow_nsfw:
        print(img_title + " is marked with NSFW. Not downloading.")
        continue

    if img_json.get('link_flair_text') == 'Mobile' and not also_mobile:
        print(img_title + " is for mobile. Not downloading.")
        continue

    elif img_title + ".png" in existing_files:
        print(img_title + " already exists.")

    else:
        img_name = img_json.get('title')
        img_link = img_json.get('url')
        try:
            with open(str(img_name) + ".png", 'wb') as handle:
                img = requests.get(img_link).content
                handle.write(img)

        except OSError:
            print('Can\'t save ' + img_name + '. Weird')
