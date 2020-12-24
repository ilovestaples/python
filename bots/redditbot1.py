import os
import praw
import time
import requests
import argparse
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

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
for sub in sub_collection:
    print("Getting content " + str(count) + " of " + str(args.limit) + "...")
    time.sleep(5)
    content = requests.get(sub["link"], headers = {'User-agent': 'testscript by u/garraf4'})
    c = content.json()
    img_url = c[0]['data']['children'][0]['data']['url_overridden_by_dest']
    b = requests.get(img_url, headers = {'User-agent': 'testscript by u/garraf4'})
    with open(_fullpath + sub["id"] + '.jpg', 'wb') as f:
        f.write(b.content)

    with open(_fullpath + sub["id"] + '.txt', 'w') as g:
        g.write("title: " + c[0]["data"]["children"][0]["data"]["title"] + "\n")

        comments = c[1]['data']['children']

        for comment in comments:
            g.write(comment["data"]["body"] + "\n")

    count += 1
