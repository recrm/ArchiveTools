# ArchiveTools

A collection of tools for archiving and analyzing the internet.

All scripts in this tool set are designed to be used with python 3. Python 2 is not supported.

## json-extractor.py

Json-json-extractor.py is a short script designed to extract a condensed CSV file from a collection of line separated JSON files. This script is designed for use with the data output of http://github.com/edsu/twarc and all of the scrappers in this project.

Json-extractor.py is a program that searches JSON files line by line and extracts specified elements. The script expects each line in a file to be a valid JSON object. As this program was primarily created to scan twarc output, all examples below assume twitter data.

Note: if .json file is actually valid json, then the entire file will be treated as a single json entry. The sole exception to this is if the root object is a list. In this case the parser will treat each entry in the list as a separate object.

Note: As of right now the parser handles newlines inside of a json object poorly. The parser assumes that all unnecessary whitespace in a .json file has been removed.

------------
### Basic usage.
------------

	python3 json-extractor.py text

This will search every .json file in the current directory and create a file 'output.csv' containing the text of every tweet it finds. The arguments are the data pieces that the extractor will extract. For example.

	python3 json-extractor.py text id created_at

This script will create a csv file with 3 columns. It will contain the text of the tweet as the first element, the id of the tweet as the second, and the created_at time stamp as the third. These labels match the json labels in the .json file exactly.

If an element is within another object separate the object and attribute by the character ":"

	user:screen_name

Will return the "screen_name" attribute inside the "user" object.

	entities:hashtags:text

Will return the "text" attribute inside the hash tags object which is itself inside the entities object. The entities object is a list. When the interpreter reaches a list it will copy the line for each entry found. So a single tweet with two hash tags will output two lines in the csv if hash tags are to be recorded.

---------------
### Other Arguments
---------------

* -h
	* Outputs the command line help screen.
	* example: python3 json-extractor.py -h

* -string
	* Limits which .json files the extractor looks in.
	* example: python3 json-extractor.py -string Rob
	* (Will only look in .json files that contain the string "Rob" in its filename.

* -path
	* Changes which folder the extractor looks in for .json files.
	* example: python3 json-extractor.py -path /path/to/folder
	* (Looks in folder /path/to/folder to find tweets.)

* -id
    * Adds duplicate detection an specified json entry.
    * example: python3 json-extractor.py -id id_str
    * (Will skip any json object that has the attribute id_str identical to an entry already scanned.)

* -NA
    * This flag will insert 'NA' into any json entry that cannot be found instead of erroring.
    * example: python3 json-extractor.py -NA optional:entry
    * (Will create insert 'NA' into any 'optional:entry' that cannot be found.

* -compress
    * Creates a new .json file instead of a csv file. Inserts all scanned entries into the output file.
    * example python3 json-extractor.py -compress -path /path/to/folder
    * (Will scan all .json files in /path/to/folder and will insert them into one large .json file.

* -output
	* Changes the name of the csv file the extractor outputs to.
	* example: python3 json-extractor.py -output Rob-Ford.csv
	* (Rob-Ford.csv will be created instead of output.csv)

* -dialect
	* Sets the format the csv file will follow. Defaults to Microsoft excel.
	* See python module csv.list_dialects() for details.

* -start
	* Allows the extractor to filter by time. If set will only record tweets
	* after start and before end (format mm:dd:yyyy).

* -end
	* example: python3 json-extractor.py -start 01:01:2014 -end 01:02:2014
	* (Records all tweets between midnight January first and midnight January second.

* -hashtag
	* Only record tweets that contain this hash tag.
	* example: python3 json-extractor.py -hashtag gamergate

--------
### Examples
--------

To grab user_name, hash tags, and text from all Rob Ford tweets in folder /path/to/folder

	python3 json-extractor.py -path /path/to/folder -string Rob user:screen_name entities:hashtags:text text

To grab all tweet text on January 1, 2014 in current folder.

	python3 json-extractor.py -start 01:01:2014 -end 01:02:2014 text

--------
### To Do
--------

- [ ] Soften the assumption that each line is a valid json object. Program should be able to find a json object even if it is pretty printed.

## imageboard-scraper.py

Imageboard-scraper.py is a simple script designed to interact with image boards based on the 4chan API. Running the program collects all posts made since the script was last run. If the script has not been run before it collects all current posts.

------------
### Basic usage.
------------

    python3 imageboard-scraper.py trv

Running the script with a single option will download all posts in the associated board. The above command will download all posts in the 4chan /trv (travel) board.

---------------
### Other Arguments
---------------

* -h
	* Outputs the command line help screen.
	* example: python3 imageboard-scraper.py -h

* -output
	* Changes the directory the scraped posts will be saved to.
	* example: python3 imageboard-scraper.py -output /path/to/save/folder
	* (Will save results in /path/to/save/folder)

* -image
	* Boolean value, if set will also download images.
	* Stores the images in a /images folder inside the output folder.

* -url
	* Changes the internal URL's of the website to scrap.
	* Currently only accepts '4chan' or '8chan'.
	* Defaults to '4chan'.

## warc-extractor.py

Warc-extractor.py is a tool designed to filter and extract files from warc archive files. This script is designed to perform three different purposes.

* Provide basic information as to what a collection of warc files contain.
* Create new warc files containing only filtered elements of old warc files.
* Dump the file contents of a warc file to disk.

------------
### Basic usage.
------------

    python3 warc-extractor.py

Running the program without any arguments scans all of the warc files in the current directory and outputs some basic information about those files.

Warc-extractor.py accepts an unlimited number of filter options. A filter option controls which warc entries the script scans.

    python3 warc-extractor.py warc-type:request

In the above example the script will output basic information about all of the warc entries where the warc header 'warc-type' is set to request (case insensitive). Substrings are allowed in the second part so 'warc-type:requ' would be equivalent while 'warc-type:re' would return both 'request' and 'response' entries.

Many warc entries also contain HTTP headers which can also be accessed by filter.

    python3 warc-extractor.py http:content-type:pdf

The above script finds all warc entries that contain PDF's. Specifically it would filter out any warc entry that does not contain an HTTP header 'content-type' that contains the string 'pdf'. (Note: imputing any HTTP filter implicitly filters out any warc entry that does not contain an HTTP request or response.)

There is also some information found in an HTTP object's version line. This information can be access via some special operators: error, command, path, status, version. The most important being error.

    python3 warc-extractor.py http:error:200

The above script would filter out any HTTP responses that did not return error code 200, as well as implicitly remove HTTP requests which do not contain error codes.

Additionally, negative searches are also allowed.

    python3 warc-extractor.py \!http:content-type:pdf

The above script would return all warc entries that do not contain contain PDF's. (Note: the '\' character is required because '!' is a reserved character in bash.)

Once you have verified that the script is only grabbing those warc entries that are required. The contents of the found warc entries can be dumped in two different ways.

    python3 warc-extractor.py some:filter -dump warc

The above script would create a new warc file containing only the filtered elements.

    python3 warc-extractor.py some:filter -dump content

The above script would attempt to extract the contents of the filtered entries. (Note: the -dump flag implicitly adds "warc-type:response" and "content-type:application/http" to the filters. As warc entries that do not match these filters do not contain file-like objects.)

---------------
### Other Arguments
---------------

* -h
	* Outputs the command line help screen.
	* example: python3 warc-extractor.py -h

* -string
	* Limits which .warc files the extractor looks in.
	* example: python3 warc-extractor.py -string archive
	* (Will only look in .warc files that contain the string "archive" in its filename.

* -path
	* Changes which folder the extractor looks in for .warc files.
	* example: python3 warc-extractor.py -path /path/to/folder
	* (Looks in folder /path/to/folder to find warc files.)

* -output_path
	* Changes the folder dumped files are placed in.
	* example: python3 warc-extractor.py -output /path/to/folder
	* (All dumped files will be placed in /path/to/folder)

* -output
	* Changes the name of the warc file the extractor outputs to.
	* example: python3 warc-extractor.py -output new-warc.warc
	* (new-warc.warc will be created instead of output.warc)

* -dump
	* Triggers output of data. Defaults to no output.
	* Choices are 'content' and 'warc'.
	* 'warc' will output all warc entries that remain after filter to 'output.warc'.
	* 'content' will output the saved file in all warc entries that remain after filter.
	* example: python3 warc-extractor.py -dump content

* -output
	* Changes the name of the warc file the extractor outputs to.
	* example: python3 warc-extractor.py -output new-warc.warc
	* (new-warc.warc will be created instead of output.warc)

* -output
	* Changes the name of the warc file the extractor outputs to.
	* example: python3 warc-extractor.py -output new-warc.warc
	* (new-warc.warc will be created instead of output.warc)

* -silence
    * Boolean variables, silences collection of index data and prevents script from writing to terminal.

* -error
    * Debugging command, see troubleshooting below.

--------
### Examples
--------

To create a warc file containing all HTTP responses that are not file-like objects.

    python3 warc-extractor.py -dump warc warc-type:response \!content-type:application/http

To dump all PDF's from a warc file to disk.

    python3 warc-extractor.py -dump content http:content-type:pdf

To dump everything a warc file contains to disk.

    python3 warc-extractor.py -dump content http:error:200

--------
### Troubleshooting
--------

Warc files are complicated and huge. Creating a single script that can properly handle all of the many strange and wonderful objects that might be hidden in a warc file is a large undertaking. Because of this bugs are inevitable.

The script contains an -error command script designed to make dealing with problematic warc entries a bit easier. If the -error tag is supplied to the script, the script will do it's best to skip all entries that cause errors then write all problematic entries to a new warc file 'error.warc'. Should this script error, please try running it again with the -error tag and then upload the resulting 'error.warc' file along with the bug report.

There are many possible problems a warc file could contain that are not limited to specific entries. In these situations the -error tag will not prevent the error and will not create the error.warc file. In these cases please still fill out a bug report. However, the problem is unlikely to be fixed unless I can get access to the warc file that created the problem.

One final note, this script was programmed and tested on a Linux platform. In theory it should work on any platform that Python 3 works on; however, I make no guarantees. Help on this issue would be greatly appreciated.
