def root_check():
	import getpass

	if getpass.getuser() == "root":
		print("Do not run tap as root. tap will ask for root permissions when it needs them.")
		quit()
