import json
import requests
import sys
import time
import os
import shutil
import argparse
import math

class Response:
    def __init__(self):
        self.time = 0
        self.rate = 1

    @staticmethod
    def current_time():
        return math.ceil(time.time())

    def get_response(self, *args, **kwargs):
        """Wrapper function for requests.get that limits rate."""
        test = self.current_time()
        while test <= self.time:
            time.sleep(1)
            test = self.current_time()

        http = requests.get(*args, **kwargs)
        self.time = self.current_time() + self.rate

        #Check for breakthrough rate limits.
        if http.status_code == 522:
            self.time +=1
            self.rate +=1
            return self.get_response(*args, **kwargs)

        return http

GET = Response()

def capture_image(post, args):
    """Downloads the image assosiated with a post."""
    if "tim" in post:
        filename = str(post['tim']) + post['ext']
        if not os.path.isfile(filename):
            url = args.url['images'].format(args.board, filename)
            img = GET.get_response(url, stream=True)
            img.raw.decode_content = True
            with open(args.output + "image/" + filename, "wb+") as im:
                shutil.copyfileobj(img.raw, im)

def posts(board, since):
    """Iterates over new posts."""

    #Get list of threads.
    url = args.url['catalog'].format(board)
    catalog = GET.get_response(url).json()

    #Iterate over posts in thread
    for page in catalog:
        for thread in page["threads"]:
            if thread['last_modified'] > since:
                iden = args.url['threads'].format(board, thread["no"])
                t = GET.get_response(iden).json()
                for post in t["posts"]:
                    if post['time'] > since:
                        yield post

def parse(args):
    #Read in previous config.
    config = args.output + "/.{}-config".format(args.board)
    since = 0
    if os.path.isfile(config):
        with open(config) as fp:
            since = int(fp.readline())
    largest_id = since

    #Create new file and insert new posts.
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(args.output + "/{}-{}.json".format(args.board, t), "w+") as fp:
        for post in posts(args.board, since):
            if post['time'] > largest_id:
                largest_id = post['time']
            json.dump(post, fp)
            fp.write("\n")
            if args.image:
                capture_image(post, args)

    #write out new config.
    with open(config, "w+") as fp:
        fp.write(str(largest_id))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrapes imageboards based on the 4chan api.')
    parser.add_argument("board", nargs=1, help="Specific image board to scrape. (ex. 'trv' for the 4chan travel board.")
    parser.add_argument("-output", default="data", help="Optional folder to output results. Defaults to 'data'.")
    parser.add_argument("-image", action="store_true", help="Set to download images.")
    parser.add_argument("-url", choices=("4chan", "8chan"), default="4chan", help="Choose which website to download from.")
    args = parser.parse_args()

    args.board = args.board[0]

    if not args.output.endswith("/"):
        args.output += "/"

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.image:
        if not os.path.exists(args.output + "image/"):
            os.makedirs(args.output + "image/")

    if args.url == "4chan":
        args.url = {
            "catalog": "http://a.4cdn.org/{}/threads.json",
            "threads": "http://a.4cdn.org/{}/thread/{}.json",
            "images": "http://i.4cdn.org/{}/{}",
        }
    elif args.url == "8chan":
        args.url = {
            "catalog": "http://8ch.net/{}/threads.json",
            "threads": "http://8ch.net/{}/res/{}.json",
            "images": "http://8ch.net/{}/src/{}",
        }

    parse(args)
