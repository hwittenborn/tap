def process_bad_apt_dependencies(apt_raw_output):
	import re

	returned_output = ""

	for i in apt_raw_output.splitlines():

		if re.search('Depends: [^ ]* but it is not installable', i) != None:

			returned_output += " " + re.sub('.*Depends: | but it is not installable', '', i)

	return returned_output
