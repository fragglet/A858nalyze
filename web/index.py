#!/usr/bin/env python

import shelve
import html

db = shelve.open("archive.db")

def statistics(post):
	"""Print statistics about post."""
	data = post["analysis"]["data"]

	lenfield = "Length: %i bytes " % len(data)
	if ((len(data) - 8) % 32) == 0:
		lenfield += "(= 8 + %i * 32)" % ((len(data) - 8) / 32)
	else:
		lenfield += "(does NOT match pattern!)"

	return html.ul(lenfield)

def file_type(post):
	return post["analysis"]["mime"]


def plain_text(post):
	"""Print plain text of post."""
	text = post["data"]["selftext"]
	return "<br>" + html.tt(html.escape(text))


decoders = [
	("Statistics",   statistics),
	("File type",    file_type),
	("Text",         plain_text),
]

def format_post(post):
	id = post["data"]["id"]
	title = post["data"]["title"]
	url = "http://www.reddit.com/r/A858DE45F56D9BC9/comments/%s" % id

	def formatted(x):
		name, callback = x
		return "%s: %s" % (name, callback(post))

	return html.h3(html.a(url, html.escape(title))) \
	     + html.ul(*map(formatted, decoders))


def gen_html():
	return html.html(
		html.head(html.title("a858 auto-analysis")),
		html.body(
			html.h1("a858 auto-analysis"),
			*map(lambda key: format_post(db[key]),
			     reversed(sorted(db.keys())))
		)
	)

#print "Content-Type: text/html"
#print

print gen_html()

