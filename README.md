# SUPER AWESOME DOCSRAPR CLOUD MACHINE#

####a [@Yuletide](http://twitter.com/yuletide) #cfaPHL production

v0.0001a

This simple command-line tool scrapes a given folder in google docs and builds a txt file suitable for feeding into a word cloud generator like:

- www.tagxedo.com/app.html (supports custom shapes!)
- http://www.wordle.net (pdf output)
- http://tagul.com/api

## Usage:
	$ python gdocs-wordcloud.py
	User: <google docs username>
	Pass: <google docs pass>
	0: Technical Notes
	1: Interviews
	2: Santa Cruz
	3: Philly
	enter index of folder to scrape: 1

## Requirements:

- A running [redis](http://redis.io/) instance (uses default connection parameters)
- [redis-py](https://github.com/andymccurdy/redis-py)
- [gdata-python-client](https://code.google.com/p/gdata-python-client/)
- [lxml](http://lxml.de)

## To install all requirements (after installing redis)

	$ sudo pip install redis
	$ sudo pip install gdata
	$ sudo pip install lxml

## Output:
output is a file called output.txt in the "files" folder