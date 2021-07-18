def install_package(mpr_url, packages, operation_string, application_name, application_version):
	import requests
	import json
	import re
	import os
	import subprocess
	import shutil
	import pathlib
	import time

	from functions.get_srcinfo_value                         import  get_srcinfo_value               # REMOVE AT PACKAGING
	from functions.install_pkg.dependency_checks             import  dependency_checks               # REMOVE AT PACKAGING
	from functions.install_pkg.get_editor_name               import  get_editor_name                 # REMOVE AT PACKAGING

	from functions.install_pkg.format_dependencies           import  format_dependencies             # REMOVE AT PACKAGING
	from functions.install_pkg.get_dependency_packages       import  get_dependency_packages         # REMOVE AT PACKAGING
	from functions.install_pkg.process_bad_apt_dependencies  import  process_bad_apt_dependencies    # REMOVE AT PACKAGING

	# This is used a bit below to get the editor required to look over build files.
	# We run this now in case an editor is specified, but it cannot be found
	# on the system (we would thus quit now, instead of when looking over the build files).
	editor_name = get_editor_name()

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

	# Check if any packages cannot be found
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
		for i in ['Depends', 'MakeDepends', 'CheckDepends']:

			try:
				dependencies_temp += mpr_rpc_json_data['results'][number][i]
			except KeyError:
				continue

		number = number + 1

	dependencies = sorted(dependencies_temp)

	# Format dependencies for APT
	apt_dependency_list = format_dependencies(dependencies)

	# Generate argument list for 'apt-get satisfy'
	apt_dependency_package_arguments = ""

	for i in apt_dependency_list:
		apt_dependency_package_arguments += f" \\''{i}'\\'"

	print('Checking dependencies...')

	# Get raw output from apt-get
	apt_raw_output = os.popen(f"eval apt-get satisfy -sq {apt_dependency_package_arguments} 2>&1").read()

	# Process previous output to figure out what we need to do
	apt_needed_dependencies = get_dependency_packages(apt_raw_output, 'The following NEW packages will be installed')
	apt_removal_dependencies = get_dependency_packages(apt_raw_output, 'The following packages will be REMOVED')

	# Quit if bad dependencies were found
	bad_apt_dependencies = process_bad_apt_dependencies(apt_raw_output)

	if bad_apt_dependencies != "":

		print()
		print("The following packages have unmet dependencies:")
		print(f" {bad_apt_dependencies}")
		quit()

	# Go over what'll be installed
	apt_package_text = ""
	for i in packages:
		apt_package_text += f" {i}"

	if apt_removal_dependencies != "":
		print()
		print('The following packages are going to be REMOVED:')
		print(f" {apt_removal_dependencies}")

	if apt_needed_dependencies != "":
		print()
		print("The following dependencies are going to be installed:")
		print(f" {apt_needed_dependencies}")

	print()
	print(f"The following packages are going to be built and {operation_string}:")
	print(f" {apt_package_text}")

	print()
	continue_status = input("Would you like to continue? [Y/n] ")

	if len(continue_status) != 0 and continue_status != 'Y' and continue_status != 'y':
		print("Quitting...")
		quit(1)

	print()

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

			# Look over the PKGBUILD before checking for other files,
			# as we want the PKGBUILD to *always* be the first file to open
			exit_code = subprocess.call(f"'{editor_name}' PKGBUILD", shell=True)

			if exit_code != 0:
				print(f"Command '{editor_name}' exited with code '{exit_code}'.")
				quit(1)

			for j in pathlib.Path("./").glob('**/*'):

				# Look at all files, excluding 'PKGBUILD', '.SRCINFO', and
				# everything in the '.git' folder
				if str(j) != 'PKGBUILD' and str(j) != '.SRCINFO' and bool(re.match('^\.git/', str(j))) == False and os.path.isfile(j) == True:
					exit_code = subprocess.call(f"'{editor_name}' '{j}'", shell=True)

					if exit_code != 0:
						print(f"Command '{editor_name}' exited with code '{exit_code}'.")
						quit(1)

			time.sleep(1)

			confirm_status = input(f"Look over files for '{i}'? [Y/n] ")

		print()

	if len(apt_needed_dependencies) > 1:
		print("Installing build dependencies...")
		apt_install_dependencies_exit_code = os.system(f"eval sudo apt-get satisfy {apt_dependency_package_arguments}")

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
