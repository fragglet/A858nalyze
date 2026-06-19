#!/usr/bin/env python

import base64
import shelve
import simplejson

db = shelve.open("archive.db", "r")
for name, contents in db.iteritems():
	print(name, type(contents))

	# Data is in binary format; to ensure the generated files are
	# ASCII clean we encode to base64 text
	if "data" in contents["analysis"]:
		data = contents["analysis"]["data"]
		del contents["analysis"]["data"]
		contents["analysis"]["data_base64"] = base64.b64encode(data)

	name = name.replace("/", "__")
	with open("dumped/%s.json" % name, "w") as f:
		f.write(simplejson.dumps(contents))
