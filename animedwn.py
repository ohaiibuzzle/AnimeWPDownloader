#!/usr/bin/env python3

import os
import requests
import re
import argparse
from platform import system

# Change these to your liking. Should work fine for everything.
parser = argparse.ArgumentParser('Command Line Arguments')

def parse_args():
    parser.add_argument('--allow-nsfw', help="Allow NSFW WP downloads", action='store_true')
    parser.add_argument('--emoji-filename', help="Save files with emoji in the name", action='store_true')
    parser.add_argument('--subreddit', type=str, help="Use a different subreddit (Use at own risk)",
                        default="https://www.reddit.com/r/Animewallpaper/")
    parser.add_argument('--down-dir', type=str, help="Directory to download to",
                        default="Downloads/")

    mb_gr = parser.add_argument_group('Mobile downloading options', '(Only really work on r/Animewallpaper)')
    mobile_opts = mb_gr.add_mutually_exclusive_group()
    mobile_opts.add_argument('--also-mobile', help="Allow mobile WP downloads", action='store_true')
    mobile_opts.add_argument('--only-mobile', help="Only allow mobile WP downloads", action='store_true')

    rd_gr = parser.add_argument_group('Sorting options')
    reddit_opts = rd_gr.add_mutually_exclusive_group()

    reddit_opts.add_argument('--new', help='Get new posts (default)', action='store_true', default=True)
    reddit_opts.add_argument('--hot', help='Get hot posts', action='store_true')
    reddit_opts.add_argument('--rising', help='Get rising posts', action='store_true')
    reddit_opts.add_argument('--top-today', help='Get top of the day posts', action='store_true')
    reddit_opts.add_argument('--top-week', help='Get top of the week posts', action='store_true')
    reddit_opts.add_argument('--top-month', help='Get top of the month posts', action='store_true')
    reddit_opts.add_argument('--top-year', help='Get top of the year posts', action='store_true')
    reddit_opts.add_argument('--top-all', help='Get all time posts', action='store_true')



def emoji_be_gone(input_string):
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
    return emoji_pattern.sub(r'', input_string)


def filename_fix(input_string: str):
    if system() == "Windows":
        return input_string.replace('/', " ") \
            .replace("\\", "") \
            .replace(':', " ") \
            .replace("\"", "\'") \
            .replace("<", "\'") \
            .replace(">", "\'") \
            .replace("|", "\'") \
            .replace("?", " ") \
            .replace("*", "\'")
    # Windows sucks
    else:
        return input_string.replace('/', " ")

def main():
    parse_args()
    args = parser.parse_args()

    down_dir = args.down_dir
    base_url = args.subreddit

    reddit_loc = ""

    if args.new:
        reddit_loc = base_url + "new.json"
    elif args.hot:
        reddit_loc = base_url + "hot.json"
    elif args.rising:
        reddit_loc = base_url + "rising.json"
    elif args.top_today:
        reddit_loc = base_url + "top.json/?t=day"
    elif args.top_week:
        reddit_loc = base_url + "top.json/?t=week"
    elif args.top_month:
        reddit_loc = base_url + "top.json/?t=month"
    elif args.top_year:
        reddit_loc = base_url + "top.json/?t=year"
    elif args.top_all:
        reddit_loc = base_url + "top.json/?t=all"


    request_header = {
        'User-Agent': 'Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36\
        (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
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
        if not args.emoji_filename:
            img_title = emoji_be_gone(img_json.get('title'))
        else:
            img_title = img_json.get('title')

        img_title = filename_fix(img_title)
        img_link = img_json.get('url')

        if not img_link.endswith(".png"):
            print(img_title + " is not an image. Not downloading.")
            continue

        if img_json.get('over_18') and not args.allow_nsfw:
            print(img_title + " is marked with NSFW. Not downloading.")
            continue

        if (img_json.get('link_flair_text') == 'Mobile' and not args.also_mobile) and not args.only_mobile:
            print(img_title + " is for mobile. Not downloading.")
            continue

        elif img_title + ".png" in existing_files:
            print(img_title + " already exists.")
            continue

        elif args.only_mobile:
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

if __name__ == '__main__':
    main()
