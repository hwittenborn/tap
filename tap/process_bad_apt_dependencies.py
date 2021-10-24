def process_bad_apt_dependencies(apt_raw_output):
	import re

	check_lines = []
	check_unmet_dependencies = False

	# Get the lines containing unmet dependencies
	for i in apt_raw_output.splitlines():

		if check_unmet_dependencies == True:

			if re.search("^ ", i) != None:
				check_lines += [i]
				continue

			else:
				break

		elif i == "The following packages have unmet dependencies:":
			check_unmet_dependencies = True
			continue


	if len(check_lines) == 0:
		return []

	returned_output = []

	for i in check_lines:
		returned_output += [re.sub('^.*Depends: | but [^ ]* is to be installed|but it is not installable', '', i)]

	return returned_output
