def check_unfindable_packages(packages, rpc_packages):
	# Check that all packages were able to be found
	bad_packages = []

	# Check against each package specified on the CLI
	for i in packages:

		# Check if any of the packages in the RPC results matches said package
		for j in rpc_packages:
			if i == j:
				i = True
				break

		if i != True:
			bad_packages += [i]

	return bad_packages
