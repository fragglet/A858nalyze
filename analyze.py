import os
import re
import tempfile

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
	return re.sub(r"\S+: ", "", system("file", data))


def hexdump(data):
	"""Perform a hex-dump of the decoded data."""
	return system("hexdump -C", data)


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


def analyze(post):
	data = decode_data(post["data"]["selftext"])

	post["analysis"] = {
		"data": data,
		"mime": file_type(data),
		"hexdump": hexdump(data),
	}
