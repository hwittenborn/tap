def arg_check(argument_list, application_name, application_version):
	import re

	from functions.help_menu   import  help_menu     # REMOVE AT PACKAGING
	from functions.root_check  import  root_check    # REMOVE AT PACKAGING

	if len(argument_list) == 0:
		help_menu(application_name, application_version)
		quit(0)

	number = 0

	argument_value = argument_list[number]

	# Process first specified option
	if argument_value == "-h" or argument_value == "--help":
		help_menu(application_name, application_version)
		quit(0)

	elif argument_value == "-V" or argument_value == "--version":
		print(f"{application_name} ({application_version})")
		quit(0)

	elif argument_value == "install":
		root_check()
		operation = "install"

	elif argument_value == "update" or argument_value == "upgrade":
		root_check()
		operation = "update"

	elif argument_value == "search":
		operation = "search"

	elif argument_value == "clone":
		operation = "clone"

	elif argument_value == "list-packages":
		operation = "list-packages"

	else:
		print(f"Unknown command '{argument_value}'")
		quit(1)

	# Specifying arrays (i.e. 'hi[1]') starts at 0 for the first argument, but
	# len() is going to start at 1 for counting, so we need to subtract one.
	argument_list_length = len(argument_list) - 1

	# Add 1 to 'number' as we're going to start processing the *second*
	# specified option.
	number = number + 1

	packages_temp = []
	argument_options = []

	# Loop through all remaining specified options
	while number <= argument_list_length:

		# Check for options ('-*' or '--*' strings)
		if argument_list[number] == "-h" or argument_list[number] == "--help":
			help_menu(application_name, application_version)
			quit(0)

		elif argument_list[number] == "-L" or argument_list[number] == "--skip-less-pipe":
			argument_options += ["no-less-pipe"]

		elif argument_list[number] == "-R" or argument_list[number] == "--rev-alpha":
			argument_options += ["rev-alpha"]

		elif argument_list[number] == "-V" or argument_list[number] == "--version":
				print(f"{application_name} ({application_version})")
				quit(0)

		elif bool(re.match('^-.*', argument_list[number])) == True:
			print(f"Unknown option '{argument_list[number]}'")
			bad_argument_option = True

		# Everything else is a package
		else:
			packages_temp += [argument_list[number]]

		number = number + 1

	try: bad_argument_option
	except NameError: bad_argument_option = False

	# Post-argument checks
	if bad_argument_option == True:
		quit(1)

	elif ( operation == "update" or operation == "list-packages" ) and len(packages_temp) != 0:
		print(f"Packages cannot be specified when using the {operation} command.")
		quit(1)

	elif (operation == "install" or operation == "search" or operation == "clone" ) and len(packages_temp) == 0:
		print("No package was specified.")
		quit(1)

	packages = sorted(packages_temp)

	# Return argument list and specified packages
	return [operation, packages, argument_options]
