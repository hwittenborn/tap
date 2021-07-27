def list_packages():
	import os
	import re

	from functions.colors import colors    # REMOVE AT PACKAGING

	dpkg_package_list_raw = os.popen("dpkg-query --show --showformat '${MPR-Package}/${Package}/${Version}\n'").read().splitlines()

	number = 0
	mpr_package_info = []

	for i in dpkg_package_list_raw:
		is_mpr_package = re.search('^[^/].*', i)

		if is_mpr_package != None:

			number = number + 1
			mpr_package_info += [is_mpr_package.group(0).split('/')]

	if number > 0:

		number_counter = 0

		for i in mpr_package_info:
			print(f"{colors.apt_green}{i[1]}{colors.white}/{i[2]}")
			print(f"  From: {i[0]}")

			number_counter = number_counter + 1

			if number_counter < number:
				print()
