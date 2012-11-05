#!/usr/bin/env python

from cgi import escape
import os
import re
import shelve
import tempfile

HEXCHARS = "0123456789abcdef"

db = shelve.open("archive.db")

def statistics(post, data):
	"""Print statistics about post."""
	result = "<ul>"
	result += "<li> Length: %i bytes " % len(data)
	if ((len(data) - 8) % 32) == 0:
		result += "(= 8 + %i * 32)" % ((len(data) - 8) / 32)
	else:
		result += "(does NOT match pattern!)"

	result += "</ul>"
	return result


def file_type(post, data):
	"""Attempt to identify file MIME type."""
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.write(data)
	tmp.close()

	with os.popen("file %s" % tmp.name) as stream:
		output = stream.read()

	os.remove(tmp.name)

	return output.replace("%s: " % tmp.name, "")


def plain_text(post, data):
	"""Print plain text of post."""
	text = post["data"]["selftext"]
	return "<br><tt> %s </tt>" % escape(text)


decoders = [
	("Statistics",   statistics),
	("File type",    file_type),
	("Text",         plain_text),
]

def decode_data(text):
	"""Decode hex-encoded data into binary."""

	result = []
	oldindex = None
	for c in text:
		c = c.lower()
		if c not in HEXCHARS:
			continue
		i = HEXCHARS.index(c)
		if oldindex is None:
			oldindex = i
		else:
			n = (oldindex << 4) | i
			result.append("%c" % n)
			oldindex = None
	return "".join(result)


def format_post(post):
	id = post["data"]["id"]
	title = post["data"]["title"]
	url = "http://www.reddit.com/r/A858DE45F56D9BC9/comments/%s" % id

	decoded = decode_data(post["data"]["selftext"])

	result = "<h3><a href='%s'>%s</a></h3>" % (url, escape(title))
	result += "<ul>"
	for name, callback in decoders:
		result += "<li> %s: %s" % (name, callback(post, decoded))
	result += "</ul>"

	return result


#print "Content-Type: text/html"
#print

print "<html>"
print "<head><title>a858 auto-analysis</title></head>"
print "<body>"

for key in reversed(sorted(db.keys())):
	print format_post(db[key])

print "</body>"
print "</html>"
