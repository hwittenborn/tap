def build_dependency_packages(mpr_rpc_json_data, resultcount):
	import os
	import shutil
	import subprocess

	from functions.get_srcinfo_value  import  get_srcinfo_value                # REMOVE AT PACKAGING
	from functions.generate_control_string  import  generate_control_string    # REMOVE AT PACKAGING

	number = 0

	while number < resultcount:

		package_name = mpr_rpc_json_data["results"][number]["Name"]
		package_version = mpr_rpc_json_data["results"][number]["Version"]

		os.mkdir(f"/var/tmp/mpm/dependency_dir/{package_name}/")
		shutil.copy2(f"/var/tmp/mpm/build_dir/{package_name}/.SRCINFO", f"/var/tmp/mpm/dependency_dir/{package_name}/.SRCINFO")

		os.chdir(f"/var/tmp/mpm/dependency_dir/{package_name}/")

		depends_packages = []

		for j in ['depends', 'makedepends', 'checkdepends', (subprocess.check_output(["lsb_release", "-cs"]) + '_depends')]:
			depends_packages += get_srcinfo_value(j, True)

		conflicts_packages = get_srcinfo_value("conflicts", False)
		replaces_packages = get_srcinfo_value("replaces", False)
		breaks_packages = get_srcinfo_value("breaks", False)
		provides_packages = get_srcinfo_value("provides", False)

		depends_control = generate_control_string("Depends", depends_packages)
		conflicts_control = generate_control_string("Conflicts", conflicts_packages)
		replaces_control = generate_control_string("Replaces", replaces_packages)
		breaks_control = generate_control_string("Breaks", breaks_packages)
		provides_control = generate_control_string("Provides", provides_packages)

		os.mkdir(f"{package_name}")
		os.mkdir(f"{package_name}/DEBIAN/")

		file = open(f"{package_name}/DEBIAN/control", "a")

		# Generate control file
		file.write(f"Package: {package_name}\n")
		file.write(f"Version: {package_version}\n")
		file.write("Architecture: any\n")
		file.write("Maintainer: Foo Bar <foo@bar.com>\n")
		file.write("Description: Foo Bar\n")

		for i in [depends_control, conflicts_control, replaces_control, breaks_control, provides_control]:
			if i != None:
				file.write(f"{i}\n")

		file.close()

		# Build dependency package
		dpkg_command = subprocess.Popen(["dpkg", "-b", f"./{package_name}"], stdout=subprocess.DEVNULL)
		dpkg_command.wait()
		dpkg_exit_code = dpkg_command.returncode

		if dpkg_exit_code != 0:
			print()
			print(f"There was an error checking dependencies for '{package_name}'.")
			quit(1)

		shutil.copy2(f"{package_name}.deb", f"/var/tmp/mpm/dependency_debs/{package_name}.deb")

		# Restart loop
		number = number + 1
