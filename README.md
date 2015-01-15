# ArchiveTools
A collection of tools for archiving and analysing the internet.

All scripts in this toolset are with and designed to be used with python3.
Python2 is not supported.

## json-extractor.py

Json-json-extractor.py is a short script designed to extract a condensed CSV
file from a collection of line separated JSON files. This script is designed
for use with the data output of https://github.com/edsu/twarc and all of the
scrappers in this project.

Json-extractor.py is a program that searches .json file line by line and extracts
specified elements. The script expects each line in a file to be a valid JSON
object. As this program was primarily created to scan twarc output, all examples
below assume twitter data.

------------
### Basic usage.
------------

	python3 json-extractor.py text

This will search every .json file in the current directory and create a file
'output.csv' containing the text of every tweet it finds.

The arguments are the data pieces that the extractor will extract. For example.

	python3 json-extractor.py text id created_at

This script will create a csv file with 3 columns. It will contain the text of
the tweet as the first element, the id of the tweet as the second, and the
created_at timestamp as the third. These lables match the json labels in the
.json file exactly.

If an element is within another object separate the object and attribute by the
character ":"

	user:screen_name

Will return the "screen_name" attribute inside the "user" object.

	entities:hashtags:text

Will return the "text" attribute inside the hashtags object which is itself
inside the entities object. The entities object is a list. When the interpreter
reaches a list it will copy the line for each entry found. So a single tweet
with two hashtags will output two lines in the csv if hashtags are to be recorded.

---------------
### Other Arguments
---------------

-h          | Outputs the command line help screen.
            |example: python3 json-extractor.py -h

-string     |Limits which .json files the extractor looks in.
            |example: python3 json-extractor.py -string Rob
            |(Will only look in .json files that contain the string "Rob" in its filename.

-path       |Changes which folder the extractor looks in for .json files.
            |example: python3 json-extractor.py -path /path/to/folder
            |(Looks in folder /path/to/folder to find tweets.)

-output     |Changes the name of the csv file the extractor outputs to.
            |example: python3 json-extractor.py -output Rob-Ford.csv
            |(Rob-Ford.csv will be created instead of output.csv)

-start      |Allows the extractor to filter by time. If set will only record
            |tweets after start and before end (format mm:dd:yyyy).

-end        |example: python3 json-extractor.py -start 01:01:2014 -end 01:02:2014
            |(Records all tweets between midnight January first and midnight January second.

-dialect    |Sets the format the csv file will follow. Defaults to microsoft
            |excel. See python module csv.list_dialects() for details.

-hashtag    |Only record tweets that contain this hashtag.
            |example: python3 json-extractor.py -hashtag gamergate
            |(Records only tweets that contain hashtag "gamergate")

--------
### Examples
--------

To grab user_name, hashtags, and text from all Rob Ford tweets in folder /path/to/folder

	python3 json-extractor.py -path /path/to/folder -string Rob user:screen_name entities:hashtags:text text

To grab all tweet text on January 1, 2014 in current folder.

	python3 json-extractor.py -start 01:01:2014 -end 01:02:2014 text

--------
### To Do
--------

- [ ] Soften the assumption that each line is a valid json object. Program should be able to find a json object even if it is pretty printed.

- [ ] If top level Json object is a list. Then the extractor should treat it as if each element of list is a top level JSON object.
