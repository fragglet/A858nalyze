#!/usr/bin/env python

import shelve
import html

db = shelve.open("../archive.db", 'r')

def statistics(post):
	"""Print statistics about post."""
	data = post["analysis"]["data"]

	lenfield = "Length: %i bytes " % len(data)
	if ((len(data) - 8) % 32) == 0:
		lenfield += "(= 8 + %i * 32)" % ((len(data) - 8) / 32)
	else:
		lenfield += "(does NOT match pattern!)"

	return html.ul(
		lenfield,
		"Statistical distribution: %s" % \
		    post["analysis"]["distribution"],
	)

def timezone_link(zone):
	return html.a(zone, href="https://en.wikipedia.org/wiki/%s" % zone)

def time_data(post):
	timedata = post["analysis"]["time"]
	return html.ul(
		"Time in post title: %s" % timedata["title_time_str"],
		"Posted to Reddit: %s UTC" % timedata["post_time_str"],
		"Identified time zone: %s" % \
		    timezone_link(timedata["timezone"]),
		"Post delay: %i seconds" % timedata["post_delay"],
	)

def file_type(post):
	mime = post["analysis"]["mime"]
	if mime == "data":
		return "unknown"
	else:
		return mime


def plain_text(post):
	"""Print plain text of post."""
	text = post["data"]["selftext"]
	return "<br>" + html.tt(html.escape(text))


decoders = [
	("Statistics",        statistics),
	("Date/time",         time_data),
	("File type (MIME)",  file_type),
	("Text",              plain_text),
]

def format_post(post):
	id = post["data"]["id"]
	title = post["data"]["title"]
	url = post["data"]["url"]

	def formatted(x):
		name, callback = x
		return "%s: %s" % (name, callback(post))

	return html.a(name=id) \
	     + html.h3(html.a(html.escape(title), href=url)) \
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

print "Content-Type: text/html"
print

print gen_html()

