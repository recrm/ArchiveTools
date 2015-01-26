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

from datetime import datetime
import json
import os
import re
import argparse
import csv
import copy
import sys
import gzip

strptime = datetime.strptime

class attriObject:
    """Class object for attribute parser."""
    def __init__(self, string, na):
        self.raw = string
        self.value = re.split(":", string)
        self.title = self.value[-1]
        self.na = na

    def getElement(self, json_object):
        found = [json_object]
        for entry in self.value:
            for index in range(len(found)):
                try:
                    found[index] = found[index][entry]
                except (TypeError, KeyError):
                    if self.na:
                        return "NA"
                    print("'{}' is not a valid json entry.".format(self.raw))
                    sys.exit()

                #If single search object is a list, search entire list. Error if nested lists.
                if isinstance(found[index], list):
                    if len(found) > 1:
                        raise Exception("Extractor currently does not handle nested lists.")
                    found = found[index]

        if len(found) == 0:
            return "NA"
        elif len(found) == 1:
            return found[0]
        else:
            return ";".join(found)

def json_entries(args):
    """Iterates over entries in path."""
    for filename in os.listdir(args.path):
        if re.match(args.string, filename) and ".json" in filename:
            f = gzip.open if filename.endswith(".gz") else open
            print("parsing", filename)
            with f(args.path + filename, 'rb') as data_file:
                for line in data_file:
                    try:
                        json_object = json.loads(line.decode(args.encoding))
                    except ValueError:
                        print("Error in", filename, "entry incomplete.")
                        continue

                    if isinstance(json_object, list):
                        for jobject in json_object:
                            yield jobject
                    else:
                        yield json_object

def parse(args):
    with open(args.output, 'w+', encoding="utf-8") as output:
        if not args.compress:
            csv_writer = csv.writer(output, dialect=args.dialect)
            csv_writer.writerow([a.title for a in args.attributes])
        count = 0
        tweets = set()

        for json_object in json_entries(args):
            #Check for duplicates
            if args.id:
                identity = args.id.getElement(json_object)
                if identity in tweets:
                    continue
                tweets.add(identity)

            #Check for time restrictions.
            if args.start or args.end:
                tweet_time = strptime(json_object['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                if args.start and args.start > tweet_time:
                    continue
                if args.end and args.end < tweet_time:
                    continue

            #Check for hashtag.
            if args.hashtag:
                for entity in json_object['entities']["hashtags"]:
                    if entity['text'].lower() == args.hashtag:
                        break
                else:
                    continue

            #compression algorithm.
            if args.compress:
                json.dump(json_object, output)
                output.write("\n")

            #Write this tweet to csv.
            else:
                item = [i.getElement(json_object) for i in args.attributes]
                csv_writer.writerow(item)

            count += 1

        print("Recorded {} items.".format(count))
        if tweets:
            print("largest id:", max(tweets))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extracts attributes from tweets.')
    parser.add_argument("attributes", nargs='*', help="Attributes to search for. Attributes inside nested inside other attributes should be seperated by a colon. Example: user:screen_name, entities:hashtags:text.")
    parser.add_argument("-string", default="", help="Regular expression for files to parse. Defaults to empty string.")
    parser.add_argument("-path", default="./", help="Optional path to folder containing tweets. Defaults to current folder.")
    parser.add_argument("-id", default="", help="Defines what entry should be used as the element id. Defaults to no id duplicate checking.")
    parser.add_argument("-na", action="store_true", help="Insert NA into absent entries instead of error.")
    parser.add_argument("-compress", action="store_true", help="Compress json archives into single file. Ignores csv column choices.")
    parser.add_argument("-output", default="output", help="Optional file to output results. Defaults to output.")
    parser.add_argument("-dialect", default="excel", help="Sets dialect for csv output. Defaults to excel. See python module csv.list_dialects()")
    parser.add_argument("-encoding", default="utf-8", help="Sets character encoding for json files. Defaults to 'utf-8'.")
    parser.add_argument("-start", default="", help="Define start date for tweets. Format (dd:mm:yyyy)")
    parser.add_argument("-end", default="", help="Define end date for tweets. Format (dd:mm:yyyy)")
    parser.add_argument("-hashtag", default="", help="Define a hashtag that must be in parsed tweets.")
    args = parser.parse_args()

    if args.compress:
        args.output += ".json"
    else:
        args.output += ".csv"

    if not args.path.endswith("/"):
        args.path += "/"

    if args.id:
        args.id = attriObject(args.id, args.NA)

    args.attributes = [attriObject(i, args.NA) for i in args.attributes]
    args.string = re.compile(args.string)

    #Tweet specific restrictions.
    args.start = strptime(args.start, '%d:%m:%Y') if args.start else False
    args.end = strptime(args.end, '%d:%m:%Y') if args.end else False
    args.hashtag = args.hashtag.lower()

    parse(args)
