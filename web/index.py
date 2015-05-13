#!/usr/bin/env python

import cgitb
cgitb.enable()

import cgi
import shelve
import html
import math

MESSAGES_PER_PAGE = 20
MIME_LINK = html.a("[Should I be excited about this?]",
                   href="http://www.reddit.com/r/Solving_A858/comments/"
                        "24vml1/mime_type/chb5k2e?context=3")

form = cgi.FieldStorage()
db = shelve.open("../archive.db", 'r')

def expander(name, inner):
	control = html.span("&#x25ba;",
	                    id="control-%s" % name,
	                    onclick='expand("%s");' % name)
	div = html.div(inner,
	               id="inner-%s" % name,
	               style="display: none;")

	return control + div

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
		"Entropy: %s" % \
		    post["analysis"]["entropy"],
		"Mean: %0.2f" % \
		    post["analysis"]["mean"],
		"Variance: %0.2f" % \
		    post["analysis"]["variance"],
		"Stdev: %0.2f" % \
		    post["analysis"]["sigma"],
		"Skewness: %0.2f" % \
		    post["analysis"]["sk"],
		"Kurtosis: %0.2f" % \
		    post["analysis"]["ex"],
	)


def histogram_grid(post):
	histogram = post["analysis"]["histogram"]
	id = post["data"]["id"]

        n = len(post["analysis"]["data"])
	p = 1 / 256.0
	expected = n * p
	stddev = math.sqrt(n * p * (1 - p))
	if stddev == 0:
		stddev = 1

	rows = []
	for y in range(16):
		row = []
		for x in range(16):
			i = y * 16 + x
			value = histogram[i]
			offset = float(value - expected) / (stddev * 8)
			bright = min(max(int(offset * 128 + 127), 0), 255)
			bgcolor = "#%02x%02x%02x" % (bright, bright, bright)
			td = html.td("&nbsp;" * 5, bgcolor=bgcolor,
			             title="0x%02x: %i" % (i, value))
			row.append(td)

		rows.append(html.tr(*row))

	return expander("histogram-grid-%s" % id, html.table(*rows))


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
		return mime + " " + MIME_LINK


def plain_text(post):
	"""Print plain text of post."""
	id = post["data"]["id"]
	text = post["data"]["selftext"]
	# Format text so that it is (usually?) four groups wide.
	# This makes it 256 bits per line.
	plaintext = html.div(html.tt(html.escape(text)), style="width: 38em;")
	return expander("plaintext-%s" % id, plaintext)


def hex_dump(post):
	"""Print hex dump of post."""
	id = post["data"]["id"]
	text = post["analysis"]["hexdump"]
	# Format text so that it is (usually?) four groups wide.
	# This makes it 256 bits per line.
	plaintext = html.pre(html.escape(text))
	return expander("hexdump-%s" % id, plaintext)


decoders = [
	("Statistics",        statistics),
	("Date/time",         time_data),
	("File type (MIME)",  file_type),
	("Text",              plain_text),
	("Hex dump",          hex_dump),
	("Histogram grid",    histogram_grid),
]


def format_post(post):
	id = post["data"]["id"]
	title = post["data"]["title"]
	url = post["data"]["url"]

	def formatted(x):
		name, callback = x
		return "%s: %s" % (name, callback(post))

	items = map(formatted, decoders) + [
		html.a("Permalink", href="/?id=%s" % id)
	]

	return html.div(html.a(name=id),
	                html.h3(html.a(html.escape(title), href=url)),
	                html.ul(*items),
	                id="post-%s" % id)


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


def list_messages():
	# Which messages to show?
	messages = list(reversed(sorted(db.keys())))
	if "start" in form:
		start = int(form["start"].value)
	else:
		start = 0
	page_messages = messages[start:start + MESSAGES_PER_PAGE]
	pager = gen_pager(messages, start)

	return html.body(
		pager,
		html.h1("a858 auto-analysis"),
		html.div(*map(lambda key: format_post(db[key]),
		              page_messages)),
		pager
	)


def single_message():
	id = form["id"].value
	for key in db.keys():
		if ("-%s-" % id) in key:
			post = db[key]
			break
	else:
		return "Unknown message: %s" % id

	return html.body(
		html.h1(html.escape(post["data"]["title"])),
		format_post(post),
	)



def gen_html():
	if "id" in form:
		body = single_message()
	else:
		body = list_messages()

	return html.html(
		html.head(
			html.title("a858 auto-analysis"),
			html.script(language='javascript', src='functions.js')
		),
		body
	)

print "Content-Type: text/html"
print

print gen_html()

