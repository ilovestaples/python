import os
import praw
import time
import requests
import argparse
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

#v0.1.1

_date = datetime.today().strftime("%b%d%Y%H%M%S")

parser = argparse.ArgumentParser()
parser.add_argument("client_id", help="client id given by reddit for this script")
parser.add_argument("client_secret", help="client secret given by reddit for this script")
parser.add_argument("user", help="user name")
parser.add_argument("password", help="password")
parser.add_argument("subreddit", help="subreddit")
parser.add_argument("time_period", help="hour, day, week, month, year or all")
parser.add_argument("limit", help="How many posts should the bot get", type=int)

args = parser.parse_args()

print("Logging in as " + args.user + "...")

reddit = praw.Reddit(client_id = args.client_id,
                    client_secret = args.client_secret,
                    username = args.user,
                    password = args.password,
                    user_agent = 'testscript by u/' + args.user)

subreddit = reddit.subreddit(args.subreddit)
top = subreddit.top(args.time_period, limit=args.limit)
sub_collection = []

for submission in top:
    sub = {}
    sub["link"] = "https://www.reddit.com/" + str(submission) + "/.json"
    sub["id"] = str(submission)
    sub_collection.append(sub)

_path = os.getcwd()
_fullpath = _path + '/content/' + args.subreddit + '/' + _date + '/'
Path(_fullpath).mkdir(parents=True, exist_ok=True)

count = 1
_headers = {'User-agent': 'testscript by u/garraf4'}
with_audio = []

for sub in sub_collection:
    print("Getting content " + str(count) + " of " + str(args.limit) + "...")
    time.sleep(5)
    content = requests.get(sub["link"], headers = _headers)
    c = content.json()

    content_url = "url"
    ext = "ext"
    audio_ext = "audio_ext"
    audio_url = "audio_url"

    is_video = c[0]['data']['children'][0]['data']['is_video']
    if is_video:
        content_url = c[0]['data']['children'][0]['data']['media']['reddit_video']['fallback_url']
        ext = ".mp4"

        audio_url = c[0]['data']['children'][0]['data']['url'] + '/DASH_audio.mp4'
        audio_ext = '.m4a'
    else:
        content_url = c[0]['data']['children'][0]['data']['url']
        ext = ".jpg"

    if is_video:
        audio = requests.get(audio_url, headers = _headers)
        if audio.status_code == 200 :
            with open(_fullpath + sub['id'] + audio_ext, 'wb') as h:
                h.write(audio.content)
            with_audio.append(sub['id'])

    b = requests.get(content_url, headers = _headers)
    with open(_fullpath + sub["id"] + ext, 'wb') as f:
        f.write(b.content)

    with open(_fullpath + sub["id"] + '.txt', 'w') as g:
        g.write("title: " + c[0]["data"]["children"][0]["data"]["title"] + "\n")

        comments = c[1]['data']['children']

        for comment in comments:
            g.write(comment["data"]["body"] + "\n")

    count += 1

os.chdir(_fullpath)

for wa in with_audio:
    os.system('ffmpeg -hide_banner -loglevel panic -y -i ' + wa + '.mp4' ' -i ' + wa + '.m4a -vcodec copy -acodec copy ' + wa + '_with_audio.mp4')
