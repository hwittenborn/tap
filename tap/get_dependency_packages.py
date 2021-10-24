def get_dependency_packages(apt_raw_output, search_string):
	import re

	apt_returned_dependencies = ""

	for i in apt_raw_output.splitlines():

		if re.search(f"{search_string}", i) != None:
			apt_dependency_list_start = True
			continue

		try:
			apt_dependency_list_start == True

			if re.search('^  ', i) != None:
				apt_returned_dependencies += i

			else:
				break

		except:
			continue

	if len(apt_returned_dependencies) == 0:
		return []

	else:
		return re.sub(' +', ' ', apt_returned_dependencies).strip().split(' ')
