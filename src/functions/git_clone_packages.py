def git_clone_packages(packages, mpr_url):
	import os

	failed_packages = " "

	for i in packages:
		git_status = os.system(f"git clone 'https://{mpr_url}/{i}.git' > /dev/null 2>&1")

		if git_status != 0:
			failed_packages += f" {i}"

			failed_packages_string =   "The following packages failed to clone\n"
			failed_packages_string += f" {failed_packages}"

			return ["Fail", failed_packages_string]

		else:
			return ["Success"]
