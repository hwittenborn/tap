def git_clone_packages(packages, mpr_url):
	import os

	failed_packages = ""
	for i in packages:
		git_status = os.system(f"git clone 'https://{mpr_url}/{i}.git' > /dev/null 2>&1")

		if git_status != 0:
			failed_packages += f"{i}, "

	if failed_packages != "":
		failed_packages = re.sub(", $", "", failed_packages)
		failed_packages_string = f"The following packages failed to clone: {failed_packages}"
		return ["Fail", failed_packages_string]
	else:
		return ["Success"]
