#!/usr/bin/env python3

# Modules
import os
import sys
import re

from functions.arg_check import arg_check                # REMOVE AT PACKAGING
from functions.help_menu import help_menu                # REMOVE AT PACKAGING
from functions.install_package import install_package    # REMOVE AT PACKAGING
from functions.update_package import update_package      # REMOVE AT PACKAGING
from functions.search_package import search_package      # REMOVE AT PACKAGING
from functions.root_check import root_check              # REMOVE AT PACKAGING

# Variables we need to function
application_name = "tap"
application_version = "git"
mpr_url = "mpr.hunterwittenborn.com"

# Argument check
if len(sys.argv) == 1:
	help_menu(application_name, application_version)
	quit(0)

argument_list = arg_check(sys.argv[1:])

number=0
argument_list_length = len(argument_list) - 1

argument_value = argument_list[number]

if argument_value == "-h" or argument_value == "--help":
	help_menu(application_name, application_version)
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

else:
	print(f"Unknown command '{argument_value}'")
	quit(1)

number = number + 1

packages_temp = []

while number <= argument_list_length:

	if argument_list[number] == "-h" or argument_list[number] == "--help":
		help_menu(application_name, application_version)
		quit(0)

	elif bool(re.match('^-.*', argument_list[number])) == True:
		print(f"Unknown option '{argument_list[number]}'")
		bad_argument_option = True

	else:
		packages_temp += [argument_list[number]]

	number = number + 1

try: bad_argument_option
except NameError: bad_argument_option = False

# Post-argument checks
if bad_argument_option == True:
	quit(1)

elif operation == "update" and len(packages_temp) != 0:
	print("Packages cannot be specified when using the update/upgrade command.")
	quit(1)

elif (operation == "install" or operation == "search" or operation == "clone" ) and len(packages_temp) == 0:
	print("No package was specified.")
	quit(1)

packages = sorted(packages_temp)

# Run commands
if operation == "install":
	install_package(mpr_url, packages, "installed", application_name, application_version)

elif operation == "update":
	update_package(mpr_url, application_name, application_version)

elif operation == "search":
	search_package(mpr_url, packages, application_name, application_version)
