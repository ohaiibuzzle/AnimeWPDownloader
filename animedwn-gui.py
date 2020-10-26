import os
import requests
import re
import argparse
import sys
from platform import system
from concurrent.futures.thread import ThreadPoolExecutor
from gooey import Gooey, GooeyParser
import signal

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


def downloader(post, args, existing_files, index):
    img_json = post.get('data')
    if not args.emoji_filename:
        img_title = emoji_be_gone(img_json.get('title'))
    else:
        img_title = img_json.get('title')

    img_title = filename_fix(img_title)
    img_link = img_json.get('url')

    if not (img_link.endswith(".png") or img_link.endswith(".jpg")):
        print("Thread: " + index + " is not an image. Not downloading.")
        sys.stdout.flush()
        return
    if img_json.get('over_18') and not args.allow_nsfw:
        print("Thread: " + index + " is marked with NSFW. Not downloading.")
        sys.stdout.flush()
        return
    if (img_json.get('link_flair_text') == 'Mobile' and not args.also_mobile) and not args.only_mobile:
        print("Thread: " + index + " is for mobile. Not downloading.")
        sys.stdout.flush()
        return
    elif img_title + ".png" in existing_files:
        print("Thread: " + index + " already exists.")
        sys.stdout.flush()
        return
    elif img_title + ".jpg" in existing_files:
        print("Thread: " + index + " already exists.")
        sys.stdout.flush()
        return
    elif args.only_mobile:
        if img_json.get('link_flair_text') != 'Mobile':
            print(index + " isn't for mobile. Not downloading.")
            sys.stdout.flush()
            return
        else:
            if img_link.endswith(".png"):
                try:
                    with open(img_title + ".png", 'wb') as handle:
                        img = requests.get(img_link).content
                        handle.write(img)
                        print("Thread" + index + " successfully downloaded something")
                        sys.stdout.flush()
                        return
                except OSError:
                    print('Thread: ' + index + ' cannot save your file')
                    sys.stdout.flush()
                    return
            elif img_link.endswith(".jpg"):
                try:
                    with open(img_title + ".jpg", 'wb') as handle:
                        img = requests.get(img_link).content
                        handle.write(img)
                        print("Thread" + index + " successfully downloaded something")
                        sys.stdout.flush()
                        return
                except OSError:
                    print('Thread: ' + index + ' cannot save your file')
                    sys.stdout.flush()
                    return
    else:
        if img_link.endswith(".png"):
            try:
                with open(img_title + ".png", 'wb') as handle:
                    img = requests.get(img_link).content
                    handle.write(img)
                    print("Thread" + index + " successfully downloaded something")
                    sys.stdout.flush()
                    return
            except OSError:
                print('Thread: ' + index + ' cannot save your file')
                sys.stdout.flush()
                return
        elif img_link.endswith(".jpg"):
            try:
                with open(img_title + ".jpg", 'wb') as handle:
                    img = requests.get(img_link).content
                    handle.write(img)
                    print("Thread" + index + " successfully downloaded something")
                    sys.stdout.flush()
                    return
            except OSError:
                print('Thread: ' + index + ' cannot save your file')
                sys.stdout.flush()
                return

@Gooey(
    program_name="AnimeWallpaper Downloader",
    program_description="Get your waifu.",
    force_stop_is_error='false',
)
def main():
    parser = GooeyParser()
    base_conf = parser.add_argument_group('Basic configuartions')
    base_conf.add_argument('--allow-nsfw', metavar="Allow NSFW downloads", help=' You naughty thing', action='store_true')
    base_conf.add_argument('--emoji-filename', metavar="Save files with emoji in the name", help=" It's pretty fun", action='store_true', default = True)
    base_conf.add_argument('--subreddit', type=str , metavar="Use a different subreddit (Use at own risk)",
                        default="https://www.reddit.com/r/Animewallpaper/")
    base_conf.add_argument(
        "--down-dir",
        default="Downloads",
        metavar="Output directory",
        help="Directory for file output",
        widget="DirChooser",
        gooey_options=dict(),
    )
    base_conf.add_argument('-t', '--thread-count', type=int, metavar="Number of concurrent threads (default: 10)", default=10)
    base_conf.add_argument('-n', '--post-count', type=int, metavar="Number of post to download (default: 25)", default=25)


    dl_opts = parser.add_argument_group('Downloading options', description='(Mobile filtering only works on Animewallpaper)', gooey_options={
        'show_border': False,
    })
    mobile_opts = dl_opts.add_mutually_exclusive_group(gooey_options={
        'initial_selection': 0,
        'show_label': False
    })
    mobile_opts.add_argument('--desktop-only', metavar="Only download desktop wallpapers", action='store_true', default = True)
    mobile_opts.add_argument('--also-mobile', metavar="Also download mobile wallpapers", action='store_true')
    mobile_opts.add_argument('--only-mobile', metavar="Only download mobile wallpapers", action='store_true')

    reddit_opts = dl_opts.add_mutually_exclusive_group(gooey_options={
        'initial_selection': 0
    })

    reddit_opts.add_argument('--new', metavar='Get new posts', action='store_true', default=True)
    reddit_opts.add_argument('--hot', metavar='Get hot posts', action='store_true')
    reddit_opts.add_argument('--rising', metavar='Get rising posts', action='store_true')
    reddit_opts.add_argument('--top-today', metavar='Get top of the day posts', action='store_true')
    reddit_opts.add_argument('--top-week', metavar='Get top of the week posts', action='store_true')
    reddit_opts.add_argument('--top-month', metavar='Get top of the month posts', action='store_true')
    reddit_opts.add_argument('--top-year', metavar='Get top of the year posts', action='store_true')
    reddit_opts.add_argument('--top-all', metavar='Get all time posts', action='store_true')

    args = parser.parse_args()

    down_dir = args.down_dir
    base_url = args.subreddit

    reddit_loc = ""

    if args.new:
        reddit_loc = base_url + "new.json" + "?limit=100"
    elif args.hot:
        reddit_loc = base_url + "hot.json" + "?limit=100"
    elif args.rising:
        reddit_loc = base_url + "rising.json" + "?limit=100"
    elif args.top_today:
        reddit_loc = base_url + "top.json/?t=day" + "&?limit=100"
    elif args.top_week:
        reddit_loc = base_url + "top.json/?t=week" + "&?limit=100"
    elif args.top_month:
        reddit_loc = base_url + "top.json/?t=month" + "&?limit=100"
    elif args.top_year:
        reddit_loc = base_url + "top.json/?t=year" + "&?limit=100"
    elif args.top_all:
        reddit_loc = base_url + "top.json/?t=all" + "&?limit=100"


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

    last_post = ""
    post_count = 0
    pool = ThreadPoolExecutor(max_workers=args.thread_count)

    sub_loc = reddit_loc

    while post_count < args.post_count:
        page = requests.get(sub_loc, headers=request_header).json()
        post_list = page.get('data').get('children')
        for _ in post_list:
            if post_count > args.post_count:
                break
            arg = [_, args, existing_files, post_count]
            pool.submit(lambda p: downloader(*p), arg)
            last_post = _.get('data').get('name')
            post_count += 1
        sub_loc = reddit_loc + "&after=" + last_post 
    pool.shutdown(wait=True)
    print("Done working!")
    return

if __name__ == '__main__':
    main()
    sys.exit(0)