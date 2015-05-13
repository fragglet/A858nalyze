import math
import os
import re
import tempfile
import time

HEXCHARS = "0123456789abcdef"

def system(command, data):
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.write(data)
	tmp.close()

	with os.popen("%s %s" % (command, tmp.name)) as stream:
		output = stream.read()

	os.remove(tmp.name)

	return output


def file_type(data):
	"""Attempt to identify file MIME type."""
	output = system("file", data)
	return re.sub(r"\S+: ", "", system("file", data)).strip()


def hexdump(data):
	"""Perform a hex-dump of the decoded data."""
	return system("hexdump -C", data)


def histogram(data):
	result = [0] * 256
	for c in data:
		result[ord(c)] += 1
	return result


def histogram_analysis(data, dist):
	# Assume a binominal distribution.
	# If any of the values is more than 6 standard deviations from
	# the mean then it may be statistically significant.

	n = len(data)
	p = 1 / 256.0
	expected = n * p
	stddev = math.sqrt(n * p * (1 - p))
	biggest_diff = 0
	for d in dist:
		diff = abs(expected - d)
		if diff > biggest_diff:
			biggest_diff = diff

	if stddev > 0:
		diff_stddev = float(biggest_diff) / stddev
	else:
		diff_stddev = 0

	if diff_stddev > 6:
		return "Possibly non-uniform (%.02f stddevs)" % diff_stddev
	else:
		return "Uniform (<= %.02f stddevs)" % diff_stddev

def analyze_time(post):
	"""Analyze time in post title."""
	title_time = time.strptime(post["data"]["title"], "%Y%m%d%H%M")
	title_time = (title_time.tm_year, title_time.tm_mon, title_time.tm_mday,
	              title_time.tm_hour, title_time.tm_min, title_time.tm_sec,
	              title_time.tm_wday, 0, 0)
	title_time_secs = time.mktime(title_time) - time.timezone
	post_time_secs = int(float(post["data"]["created_utc"]))
	post_time = time.gmtime(post_time_secs)

	# Offset of time in title from the UTC post time gives the time zone.
	# Round to nearest time zone.

	if title_time_secs < post_time_secs:
		tz_hours = int((title_time_secs - post_time_secs - 1800) / 3600)
	else:
		tz_hours = int((title_time_secs - post_time_secs + 1800) / 3600)

	if tz_hours < 0:
		tz = "UTC%i" % tz_hours
	elif tz_hours == 0:
		tz = "UTC"
	else:
		tz = "UTC+%i" % tz_hours

	# Assume the messages are posted by an automated script; if the
	# script starts running at the head of the minute, it will take
	# a short amount of time to start, construct the message and
	# post to Reddit. What is the difference in seconds between the
	# time in the title and the time when the message was posted?

	post_delay = post_time_secs - (title_time_secs - tz_hours * 3600)

	return {
		"title_time" : tuple(title_time),
		"title_time_str" : time.asctime(title_time),
		"post_time_str" : time.asctime(post_time),
		"timezone" : tz,
		"post_delay" : post_delay,
	}


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


def mean(data):
	n = len(data)
	if n == 0:
		return 0

	result = 0
	for c in data:
		result += ord(c)
	return float(result) / float(n)

def variance(data, mean):
	n = len(data)
	if n == 0:
		return 0

	result = 0
	for c in data:
		result += math.pow((ord(c) - mean), 2)
	return result / n

def skewness(data, mean, sigma):
	n = len(data)
	if n == 0 or sigma == 0:
		return 0

	result = 0
	for c in data:
		result += math.pow((ord(c) - mean),3)
	return (result / n) / math.pow(sigma,3)

def excess(data, mean, sigma):
	n = len(data)
	if n == 0 or sigma == 0:
		return 0

	result = 0
	for c in data:
		result += math.pow((ord(c) - mean),4)
	return ((result / n) / math.pow(sigma, 4)) - 3

def probabilities(data, dist):
	result = [0] * 256
	n = len(data)
	if n > 0:
		for c in range(256):
			result[c] = float(dist[c]) / float(n)
	return result

def entropy(prob):
	ent = 0
	for p in prob:
		if (p != 0):
			ent += p * math.log(1 / p,2)
	return "%0.2f bits per byte" % ent

def analyze(post):
	data = decode_data(post["data"]["selftext"])
	dist = histogram(data)
	prob = probabilities(data, dist)
	meann = mean(data)
	variancen = variance(data, meann)
	sigma = math.sqrt(variancen)
	sk = skewness(data, meann, sigma)
	ex = excess(data, meann, sigma)

	post["analysis"] = {
		"data": data,
		"histogram": dist,
		"distribution": histogram_analysis(data, dist),
		"entropy": entropy(prob),
		"mean": meann,
		"variance": variancen,
		"sigma": sigma,
		"sk": sk,
		"ex": ex,
		"mime": file_type(data),
		"hexdump": hexdump(data),
		"time": analyze_time(post),
	}
