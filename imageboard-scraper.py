#!/usr/bin/env python3
"""
    warc-extractor, a simple command line tool for expanding warc files.
    Copyright (C) 2014  Ryan Chartier

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re
import sys
import time
import os
import shutil
import argparse
import math
import requests

class Response:
    def __init__(self):
        self.error = 0

    @staticmethod
    def current_time():
        return math.ceil(time.time())

    def get_response(self, *args, **kwargs):
        """Wrapper function for requests.get that limits rate."""
        http = requests.get(*args, **kwargs)

        if http.status_code == 200:
            #All is well.
            return http

        elif http.status_code == 522:
#            "We are being rate limited.
            print("We are being rate limited. Waiting for 30 seconds.")
            time.sleep(30)
            return self.get_response(*args, **kwargs)

        elif http.status_code == 404:
            #Thread has been deleted.
            print("Thread not found.")
            return False

        elif self.error < 50:
            time.sleep(10)
            print("Error detected '{}'.".format(http.status_code))
            self.error +=1
            return self.get_response(*args, **kwargs)

        else:
            print("Too many errors.")
            raise Exception

GET = Response()

def capture_image(post, args):
    """Downloads the image assosiated with a post."""
    if "tim" in post:
        filename = str(post['tim']) + post['ext']
        if not os.path.isfile(args.output + "image/" + filename):
            url = args.url['images'].format(args.board, filename)
            img = GET.get_response(url, stream=True)
            if img:
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
                t = GET.get_response(iden)
                if t:
                    for post in t.json()["posts"]:
                        if post['time'] > since:
                            yield post

def get_since(args):
    """
    infer last scrape based on other scrapes.
    """
    other_archive_files = []
    for filename in os.listdir(args.output):
        if re.match("^{}-\d+\.json(\.gz)?$".format(args.board), filename):
            other_archive_files.append(filename)
    other_archive_files.sort()

    since_id = None
    while len(other_archive_files) != 0:
        f = other_archive_files.pop()
        if os.path.getsize(args.output + ("/") + f) > 0:
            since_id = f

    if not since_id:
        return 0

    since = since_id.rstrip(".gz").rstrip(".json").lstrip(args.board).lstrip("-")
    t = time.strptime(since, "%Y%m%d%H%M%S")
    return int(time.mktime(t))


def parse(args):
    #Read in previous config.
    since = get_since(args)

    #Create new file and insert new posts.
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(args.output + "/{}-{}.json".format(args.board, t), "w+") as fp:
        for post in posts(args.board, since):
            json.dump(post, fp)
            fp.write("\n")
            if args.image:
                capture_image(post, args)

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
