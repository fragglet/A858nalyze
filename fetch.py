#!/usr/bin/env python

from analyze import analyze
import shelve
import simplejson
import sys
import urllib

FETCH_URL = "http://www.reddit.com/r/A858DE45F56D9BC9/.json"

class FetchException(Exception):
	pass

class A8URLOpener(urllib.URLopener):
	version = 'A858 Auto-indexer by /u/fragglet'

db = shelve.open("archive.db")

def fetch(url):
	"""Fetch JSON data from the given URL."""
	opener = A8URLOpener()
	stream = opener.open(url)
	data = stream.read()
	stream.close()

	try:
		decoded = simplejson.loads(data)
		return decoded
	except:
		raise FetchException("Failed to fetch from %s: %s" % (url, data))

def save_post(post):
	"""Save a post into the database."""
	id = post["data"]["id"]
	created = post["data"]["created_utc"]
	title = post["data"]["title"]

	# Combine data to create the key. This allows us to show some
	# basic info on the website without needing to fetch all data.

	key = "%i-%s-%s" % (int(created), id, title)

	# Store new post? Only if we didn't already save it.
	# Perform analysis functions on post.

	if key not in db:
		analyze(post)
		db[key] = post

	db.sync()

