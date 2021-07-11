def install_package(mpr_url, packages, operation_string, application_name, application_version):
	import requests
	import json
	import re
	import os
	import shutil
	import pathlib
	import time

	from functions.get_srcinfo_value import get_srcinfo_value    # REMOVE AT PACKAGING

	# Make request to MPR
	rpc_request_arguments = ""

	for i in packages:
		rpc_request_arguments += "&arg[]=" + i

	mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=info{rpc_request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})

	# Make sure returned JSON is valid
	try: mpr_rpc_json_data = json.loads(mpr_rpc_request.text)
	except json.decoder.JSONDecodeError:
		print("[JSON] There was an error processing your request.")
		quit(1)

	# Used throughout the rest of the script
	resultcount = mpr_rpc_json_data['resultcount']

	number = 0
	package_names = []

	# Get package names
	while number < resultcount:
		package_names += [mpr_rpc_json_data['results'][number]['Name']]
		number = number + 1

	# Check if any packages couldn't be found
	bad_packages = ""

	for i in packages:
		for j in package_names:
			if i == j:
				i = True
				break

		if i != True:
			bad_packages += " " + i

	if len(bad_packages) != 0:
		print("Couldn't find the following packages:")
		print(" " + str(bad_packages))
		quit(1)

	# Get dependencies for all packages
	dependencies_temp = []

	number = 0
	while number < resultcount:
		for i in ['Depends', 'Makedepends', 'Checkdepends']:

			try: dependencies_temp += mpr_rpc_json_data['results'][number][i]
			except KeyError:
				continue

		number = number + 1

	dependencies = sorted(list(set(dependencies_temp)))

	# Format dependencies for APT
	apt_package_arguments_temp = []
	for i in dependencies:

		for j in ['<=', '>=', '<', '>', '=']:

			try:
				relationship_type = re.search(j, i).group(0)
				break

			except AttributeError:
				if j == '=':
					# Needs to be set to a relationship (even when non is found)
					# for the regex check on 'package_version' below.
					relationship_type = "="
				continue

		try:
			dependency_name = re.search(f"^.*{relationship_type}", i).group(0).replace(relationship_type, '')
			dependency_version = re.search(f"{relationship_type}.*$", i).group(0).replace(relationship_type, '')

			apt_package_arguments_temp += [f"\\''{dependency_name} ({relationship_type} {dependency_version})'\\'"]

		except AttributeError:
			apt_package_arguments_temp += [f"\\''{i}'\\'"]

	apt_package_arguments = ""
	for i in apt_package_arguments_temp:
		apt_package_arguments += f" {i}"

	print('Checking dependencies...')

	apt_output = os.popen(f"eval echo apt-get satisfy -sq {apt_package_arguments} 2>&1").read()

	# Check for any dependencies that cannot be installed
	try:
		apt_bad_dependencies = re.search('Depends: .*', apt_output).group(0).replace('Depends: ', '').replace(' but it is not installable', '')

		print("The following dependencies are unable to be installed:")
		print(f"  {apt_bad_dependencies}")
		quit(1)

	except:
		pass

	# Get dependencies that need to be installed
	apt_needed_dependencies = os.popen(f"echo \"{apt_output}\" | sed 's|$| |g' | tr -d '\n' | grep -o 'The following NEW packages.*not upgraded.' | sed 's|The following NEW packages will be installed:||' | sed 's|[[:digit:]] upgraded.*||' | xargs").read()

	package_text = " "
	for i in packages:
		package_text += f" {i}"

	print()

	# Go over what'll be installed
	if len(apt_needed_dependencies) > 1:
		print("The following dependencies are going to be installed:")
		print(f"  {apt_needed_dependencies}")
		print(f"The following packages are going to be built and {operation_string}:")
		print(f" {package_text}")

	else:
		print(f"The following packages are going to be built and {operation_string}:")
		print(f" {package_text}")

	print()
	continue_status = input("Would you like to continue? [Y/n] ")

	if len(continue_status) != 0 and continue_status != 'Y' and continue_status != 'y':
		print("Quitting...")
		quit(1)

	if os.path.exists('/var/tmp/mpm/'):

		if os.access('/var/tmp/mpm/', os.W_OK) == False:
			print("Couldn't delete old build directory. Aborting...")
			quit(1)

		print("Removing old build directory...")
		shutil.rmtree('/var/tmp/mpm/')

	print("Creating build directory...")
	os.makedirs('/var/tmp/mpm/debs/')
	os.makedirs('/var/tmp/mpm/build_dir/')

	os.chdir('/var/tmp/mpm/build_dir/')

	print("Cloning packages...")
	failed_packages = " "

	for i in packages:
		git_status = os.system(f"git clone 'https://{mpr_url}/{i}.git' > /dev/null 2>&1")

		if git_status != 0:
			failed_packages += f" {i}"

	if len(failed_packages) > 1:
		print("The following packages failed to clone:")
		print(f" {failed_packages}")
		quit(1)

	print()

	for i in packages:
		os.chdir(f"/var/tmp/mpm/build_dir/{i}")

		confirm_status = input(f"Look over files for '{i}'? [Y/n] ")

		file_list = []

		while confirm_status != 'n' and confirm_status != 'N':

			for j in pathlib.Path("./").glob('**/*'):

				if bool(re.match('^\.git/', str(j))) == False and os.path.isfile(j) == True and bool(str(j) != '.SRCINFO') == True:
					os.system(f"nano '{j}'")

			time.sleep(1)

			confirm_status = input(f"Look over files for '{i}'? [Y/n] ")

		print()

	if len(apt_needed_dependencies) > 1:
		print("Installing build dependencies...")
		apt_install_dependencies_exit_code = os.system(f"eval sudo apt-get satisfy {apt_package_arguments}")

		if apt_install_dependencies_exit_code != 0:
			print("There was an error installing build dependencies.")
			quit(1)

		print()

	print("Building packages...")

	apt_installation_list = ""

	for i in packages:
		os.chdir(f"/var/tmp/mpm/build_dir/{i}")

		mpr_control_fields = os.popen('/usr/bin/env bash -c \'source PKGBUILD; echo "${control_fields}" | sed "s| |\\n|g" | grep "^MPR-Package:"\'').read()

		if len(mpr_control_fields) > 0:
			makedeb_exit_code = os.system("makedeb -v")

		else:
		 	makedeb_exit_code = os.system("makedeb -vH 'MPR-Package: True'")

		if makedeb_exit_code != 0:
		 	print(f"There was an issue building package '{i}'. Aborting...")
		 	quit(1)

		# Get package version
		package_control_version = os.popen("/usr/bin/env bash -c 'source PKGBUILD; if [[ \"$(type -t pkgver)\" == \"function\" ]]; then pkgver; fi'").read()

		if len(package_control_version) == 0:
			package_version = get_srcinfo_value('pkgver')[0]

		else:
			package_version = package_control_version

		# Get package relationship
		package_relationship = get_srcinfo_value('pkgrel')[0]

		# Get system architecture
		system_architecture = os.popen("dpkg --print-architecture").read().strip()

		# Get built package names
		package_names = get_srcinfo_value('pkgname')

		# Get built archive architecure
		package_architecture = get_srcinfo_value('arch')[0]

		if package_architecture == 'any':
			package_architecture = 'all'

		else:
			package_architecture = system_architecture

		# Copy built debs to temp directory for installation
		for j in package_names:
			shutil.move(f"/var/tmp/mpm/build_dir/{i}/{j}_{package_version}-{package_relationship}_{package_architecture}.deb", f"/var/tmp/mpm/debs/{j}_{package_version}-{package_relationship}_{package_architecture}.deb")
			apt_installation_list += f" \\''./{j}_{package_version}-{package_relationship}_{package_architecture}.deb'\\'"


	# Install packages
	print("Installing packages...")
	os.chdir("/var/tmp/mpm/debs/")
	apt_exit_code = os.system(f"eval sudo apt install {apt_installation_list}")

	if apt_exit_code != 0:
		print("There was an error installation the packages.")
		quit(1)

	print('Done.')
	quit(0)
