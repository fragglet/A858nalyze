#!/usr/bin/env python

from cgi import escape
import shelve

db = shelve.open("archive.db")

def statistics(post):
	"""Print statistics about post."""
	data = post["analysis"]["data"]
	result = "<ul>"
	result += "<li> Length: %i bytes " % len(data)
	if ((len(data) - 8) % 32) == 0:
		result += "(= 8 + %i * 32)" % ((len(data) - 8) / 32)
	else:
		result += "(does NOT match pattern!)"

	result += "</ul>"
	return result


def file_type(post):
	return post["analysis"]["mime"]


def plain_text(post):
	"""Print plain text of post."""
	text = post["data"]["selftext"]
	return "<br><tt> %s </tt>" % escape(text)


decoders = [
	("Statistics",   statistics),
	("File type",    file_type),
	("Text",         plain_text),
]

def format_post(post):
	id = post["data"]["id"]
	title = post["data"]["title"]
	url = "http://www.reddit.com/r/A858DE45F56D9BC9/comments/%s" % id

	result = "<h3><a href='%s'>%s</a></h3>" % (url, escape(title))
	result += "<ul>"
	for name, callback in decoders:
		result += "<li> %s: %s" % (name, callback(post))
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
