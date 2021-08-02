def list_packages(argument_options):
	import os
	import re

	from functions.colors 				  import  colors                 # REMOVE AT PACKAGING
	from functions.check_argument_option  import  check_argument_option  # REMOVE AT PACKAGING

	dpkg_package_list_raw = os.popen("dpkg-query --show --showformat '///${MPR-Package}///${Package}///${Version}///${Description}///${Maintainer}\n'").read().splitlines()

	number = 0
	mpr_package_info = []

	for i in dpkg_package_list_raw:
		is_mpr_package = re.search('^///[^/].*', i)

		if is_mpr_package != None:

			number = number + 1
			mpr_package_info += [is_mpr_package.group(0).split('///')]

	if number > 0:

		list_packages_output_temp = ""
		number_counter = 0

		for i in mpr_package_info:

			list_packages_output_temp += f"{colors.apt_green}{i[2]}{colors.white}/{i[3]}\n"
			list_packages_output_temp += f"  From: {i[1]}\n"
			list_packages_output_temp += f"  Description: {i[4]}\n"
			list_packages_output_temp += f"  Maintainer: {i[5]}\n"

			list_packages_output_temp += "\n"

			number_counter = number_counter + 1

		# Remove trailing newlines
		list_packages_output = list_packages_output_temp.strip()

		# Get height of terminal and number of lines in package output
		terminal_height = os.get_terminal_size()[1]
		list_packages_output_lines = list_packages_output.count('\n')

		# Pipe output into 'less' if output is greater than terminal height
		# so we don't flood the user's terminal with text.
		#
		# Also add a header at the top so the user knows where they're at.
		#
		# This gets ignored when the '--skip-less-pipe' option is passed.
		if list_packages_output_lines > terminal_height and check_argument_option(argument_options, "no-less-pipe") == False:

			# Define header
			less_header =  "==================================\n"
			less_header += "Installed MPR Packages\n"
			less_header += "Press / to search\n"
			less_header += "Press q to return to your terminal\n"
			less_header += "==================================\n\n"

			# Print output
			os.system(f"printf '{less_header}{list_packages_output}' | less -r")

		else:
			print(list_packages_output)
