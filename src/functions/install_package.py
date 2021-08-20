def install_package(mpr_url, packages, operation_string, application_name, application_version):
	import requests
	import json
	import re
	import os
	import subprocess
	import shutil
	import pathlib
	import time

	from functions.get_srcinfo_value             import  get_srcinfo_value               # REMOVE AT PACKAGING
	from functions.get_control_field_value       import  get_control_field_value         # REMOVE AT PACKAGING
	from functions.get_editor_name               import  get_editor_name                 # REMOVE AT PACKAGING
	from functions.builddir_del_err              import  builddir_del_err                # REMOVE AT PACKAGING
	from functions.colors                        import  colors                          # REMOVE AT PACKAGING
	from functions.message                       import  message                         # REMOVE AT PACKAGING

	from functions.format_dependencies           import  format_dependencies             # REMOVE AT PACKAGING
	from functions.get_dependency_packages       import  get_dependency_packages         # REMOVE AT PACKAGING
	from functions.process_bad_apt_dependencies  import  process_bad_apt_dependencies    # REMOVE AT PACKAGING
	from functions.build_dependency_packages     import  build_dependency_packages       # REMOVE AT PACKAGING
	from functions.git_clone_packages            import  git_clone_packages              # REMOVE AT PACKAGING
	from functions.make_mpr_request              import  make_mpr_request                # REMOVE AT PACKAGING
	from functions.check_unfindable_packages     import  check_unfindable_packages       # REMOVE AT PACKAGING
	from functions.generate_apt_styled_text      import  generate_apt_styled_text        # REMOVE AT PACKAGING

	# This is used a bit below to get the editor required to look over build files.
	# We run this now in case an editor is specified, but it cannot be found
	# on the system (we would thus quit now, instead of when looking over the build files).
	editor_name = get_editor_name()

	# Set user-defined packages. This to prevent any muckiness when reviewing
	# what is going to be installed when MPR dependencies are being installed.
	user_defined_packages = packages

	# Make request to MPR
	mpr_rpc_json_data = make_mpr_request(packages, mpr_url, application_name, application_version)

	resultcount = mpr_rpc_json_data['resultcount']

	number = 0

	# We use 'master_package_names' to get the full list of installed debs
	# when installing MPR dependencies. 'package_names' will only contain
	# first-level MPR packages (excluding MPR dependencies), so we store values
	# for first-level MPR packages in both variables.
	master_package_names = []
	package_names = []
	package_versions = []

	while number < resultcount:
		master_package_names += [mpr_rpc_json_data['results'][number]['Name']]
		package_names += [mpr_rpc_json_data['results'][number]['Name']]
		package_versions += [mpr_rpc_json_data['results'][number]['Version']]
		number = number + 1

	unknown_packages = check_unfindable_packages(packages, package_names)

	if len(unknown_packages) != 0:
		unknown_packages_output = ""

		for i in unknown_packages:
			unknown_packages_output += f"{i}, "

		unknown_packages_output = re.sub(", $", "", unknown_packages_output)
		message("error", f"Couldn't find the following packages: {unknown_packages_output}")
		quit()


	# Make sure build directory doesn't exist, and remove it if otherwise
	if os.path.exists('/var/tmp/mpm/'):

		message("info", "Removing old build directory...")
		shutil.rmtree('/var/tmp/mpm/', onerror=builddir_del_err)

	os.mkdir("/var/tmp/mpm/")

	# Clone packages
	message("info", "Cloning packages...")

	os.mkdir("/var/tmp/mpm/build_dir/")
	os.chdir("/var/tmp/mpm/build_dir/")

	git_clone_status = git_clone_packages(packages, mpr_url)

	if git_clone_status[0] == "Fail":
		message("error", git_clone_status[1])
		quit(1)

	# Check build dependencies
	message("info", "Checking build dependencies...")

	os.mkdir("/var/tmp/mpm/dependency_debs/")
	os.mkdir("/var/tmp/mpm/dependency_dir/")

	build_dependency_packages(mpr_rpc_json_data, resultcount)

	os.chdir("/var/tmp/mpm/dependency_debs/")

	# Generate file listing for APT
	apt_dependency_package_list = ""

	for i in package_names:
		apt_dependency_package_list += f" ./{i}.deb"

	# Check dependency listing with APT
	apt_raw_output = os.popen(f"apt-get install --dry-run {apt_dependency_package_list} 2>&1").read()

	# Check MPR for any dependencies that couldn't be found
	bad_apt_dependencies = process_bad_apt_dependencies(apt_raw_output)

	while len(bad_apt_dependencies) != 0:
		bad_apt_dependencies_no_ver = []

		# Remove relationships from output of 'bad_apt_dependencies'
		for i in bad_apt_dependencies:
			bad_apt_dependencies_no_ver += [re.sub(" \([^)]*\)", "", i)]

		bad_apt_dependencies = bad_apt_dependencies_no_ver

		mpr_rpc_json_data = make_mpr_request(bad_apt_dependencies, mpr_url, application_name, application_version)

		resultcount = mpr_rpc_json_data['resultcount']
		number = 0

		package_names = []

		while number < resultcount:
			master_package_names += [mpr_rpc_json_data['results'][number]['Name']]
			package_names += [mpr_rpc_json_data['results'][number]['Name']]
			number = number + 1

		unfindable_dependencies = check_unfindable_packages(bad_apt_dependencies, package_names)

		# Abort if there were dependencies that still couldn't be found
		if len(unfindable_dependencies) != 0:
			unfindable_dependencies_string = ""

			for i in unfindable_dependencies:
				unfindable_dependencies_string += f"{i}, "

			unfindable_dependencies_string = re.sub(", $", "", unfindable_dependencies_string)
			message("error", f"The following dependencies were unable to be found: {unfindable_dependencies_string}")
			quit(1)

		# If all dependencies were found, continue with cloning and checking them
		message("info", "Cloning additional dependencies from the MPR...")

		os.chdir("/var/tmp/mpm/build_dir/")
		git_clone_status = git_clone_packages(bad_apt_dependencies, mpr_url)

		if git_clone_status[0] == "Fail":
			message("error", git_clone_status[1])
			quit(1)

		message("info", "Rechecking build dependencies against MPR packages...")
		build_dependency_packages(mpr_rpc_json_data, resultcount)

		os.chdir("/var/tmp/mpm/dependency_debs/")

		# Generate file listing for APT
		apt_dependency_package_list = ""

		for i in master_package_names:
			apt_dependency_package_list += f" ./{i}.deb"

			# Check dependency listing with APT
			apt_raw_output = os.popen(f"apt-get install --dry-run {apt_dependency_package_list} 2>&1").read()

			# Check MPR for any dependencies that couldn't be found
			bad_apt_dependencies = process_bad_apt_dependencies(apt_raw_output)

	# Process APT's output to figure out what we need to do
	apt_removal_dependencies = get_dependency_packages(apt_raw_output, "The following packages will be REMOVED")
	apt_needed_dependencies = get_dependency_packages(apt_raw_output, "The following additional packages will be installed")
	apt_upgraded_dependencies = get_dependency_packages(apt_raw_output, "The following packages will be upgraded")
	apt_newly_installed = get_dependency_packages(apt_raw_output, "The following NEW packages will be installed")

	# Go over what'll be installed
	apt_package_text = ""
	for i in packages:
		apt_package_text += f" {i}"

	print(colors.bold)

	if len(apt_removal_dependencies) != 0:
		print(generate_apt_styled_text("The following package are going to be REMOVED:", apt_removal_dependencies))
		print()

	if len(apt_needed_dependencies) != 0:
		print(generate_apt_styled_text(f"The following additional packages are going to be installed:", apt_needed_dependencies))
		print()

	if len(apt_upgraded_dependencies) != 0:
		print(generate_apt_styled_text("The following packages will be upgraded:", apt_upgraded_dependencies))
		print()

	print(generate_apt_styled_text(f"The following packages are going to be built:", master_package_names))
	print()

	print(f"{len(master_package_names)} to build, {len(apt_upgraded_dependencies)} to upgrade, {len(apt_newly_installed)} to newly install and {len(apt_removal_dependencies)} to remove.")
	print(colors.white)

	question_string = message("question", "Would you like to continue? [Y/n] ", value_return=True)
	continue_status = input(question_string + colors.bold)
	print(colors.white)

	if len(continue_status) != 0 and continue_status != 'Y' and continue_status != 'y':
		message("info", "Quitting...")
		quit(1)

	print()

	for i in master_package_names:
		os.chdir(f"/var/tmp/mpm/build_dir/{i}")

		question_string = message("question", f"Look over files for '{i}'? [Y/n] ", value_return=True)
		confirm_status = input(question_string + colors.bold)
		print(colors.white)

		file_list = []

		while confirm_status != 'n' and confirm_status != 'N':

			# Look over the PKGBUILD before checking for other files,
			# as we want the PKGBUILD to *always* be the first file to open
			exit_code = subprocess.call(f"'{editor_name}' PKGBUILD", shell=True)

			if exit_code != 0:
				message("error", f"Command '{editor_name}' exited with code '{exit_code}'.")
				quit(1)

			for j in pathlib.Path("./").glob('**/*'):

				# Look at all files, excluding 'PKGBUILD', '.SRCINFO', and
				# everything in the '.git' folder
				if str(j) != 'PKGBUILD' and str(j) != '.SRCINFO' and bool(re.match('^\.git/', str(j))) == False and os.path.isfile(j) == True:
					exit_code = subprocess.call(f"'{editor_name}' '{j}'", shell=True)

					if exit_code != 0:
						message("error", f"Command '{editor_name}' exited with code '{exit_code}'.")
						quit(1)

			time.sleep(1)

			question_string = message("question", f"Look over files for '{i}'? [Y/n] ", value_return=True)
			confirm_status = input(question_string + colors.bold)
			print(colors.white)

		print()

	if len(apt_needed_dependencies) > 1:
		apt_dependency_package_arguments = ""

		for i in apt_needed_dependencies:
			apt_dependency_package_arguments += f"'{i}' "

		message("info", "Installing build dependencies...")
		apt_install_dependencies_exit_code = os.system(f"eval sudo apt-get satisfy {apt_dependency_package_arguments}")

		if apt_install_dependencies_exit_code != 0:
			message("error", "There was an error installing build dependencies.")
			quit(1)

		print()

	os.mkdir("/var/tmp/mpm/debs/")

	message("info", "Building packages...")

	apt_installation_list = ""

	for i in master_package_names:
		os.chdir(f"/var/tmp/mpm/build_dir/{i}")

		mpr_control_fields = os.popen('/usr/bin/env bash -c \'source PKGBUILD; echo "${control_fields}" | sed "s| |\\n|g" | grep "^MPR-Package:"\'').read()

		if len(mpr_control_fields) > 0:
			makedeb_exit_code = os.system("makedeb -v")

		else:
		 	makedeb_exit_code = os.system(f"makedeb -vH 'MPR-Package: {i}'")

		if makedeb_exit_code != 0:
		 	message("error", f"There was an issue building package '{i}'. Aborting...")
		 	quit(1)

		# Get package version
		package_control_version = get_control_field_value(i, "Version")

		# Get built package names
		package_names = get_srcinfo_value('pkgname', False)

		# Get built archive architecure
		package_architecture = get_control_field_value(i, "Architecture")

		# Copy built debs to temp directory for installation
		for j in package_names:
			shutil.move(f"/var/tmp/mpm/build_dir/{i}/{j}_{package_control_version[0]}_{package_architecture[0]}.deb", f"/var/tmp/mpm/debs/{j}_{package_control_version[0]}_{package_architecture[0]}.deb")
			apt_installation_list += f" \\''./{j}_{package_control_version[0]}_{package_architecture[0]}.deb'\\'"


	# Install packages
	message("info", "Installing packages...")
	os.chdir("/var/tmp/mpm/debs/")
	apt_exit_code = os.system(f"eval sudo apt-get reinstall {apt_installation_list}")

	if apt_exit_code != 0:
		print("There was an error installation the packages.")
		quit(1)

	print('Done.')
	quit(0)
