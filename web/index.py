#!/usr/bin/env python

import cgitb
cgitb.enable()

import cgi
import shelve
import html

MESSAGES_PER_PAGE = 20

form = cgi.FieldStorage()
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
	# Format text so that it is (usually?) four groups wide.
	# This makes it 256 bits per line.
	return "<br>" + html.div(html.tt(html.escape(text)),
	                         style="width: 38em;")


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


def gen_pager(messages, position):
	num_pages = (len(messages) + MESSAGES_PER_PAGE - 1) / MESSAGES_PER_PAGE
	this_page = position / MESSAGES_PER_PAGE

	result = []
	for i in range(num_pages):
		label = "%i" % (i + 1)
		if this_page == i:
			result.append(label)
		else:
			if i == 0:
				url = "/"
			else:
				url = "/?start=%i" % (i * MESSAGES_PER_PAGE)

			result.append(html.a(label, href=url))

	return html.div("Page: ", *(" ".join(result)),
	                style="float: right; width: 50%; text-align: right;")


def gen_html():
	# Which messages to show?
	messages = list(reversed(sorted(db.keys())))
	if "start" in form:
		start = int(form["start"].value)
	else:
		start = 0
	page_messages = messages[start:start + MESSAGES_PER_PAGE]
	pager = gen_pager(messages, start)

	return html.html(
		html.head(html.title("a858 auto-analysis")),
		html.body(
			pager,
			html.h1("a858 auto-analysis"),
			html.div(*map(lambda key: format_post(db[key]),
			         page_messages)),
			pager
		)
	)

print "Content-Type: text/html"
print

print gen_html()

