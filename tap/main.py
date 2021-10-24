#!/usr/bin/env python3

def main():
    # Modules
    import os
    import sys
    import re
    import subprocess

    from tap.split_args             import  split_args             # REMOVE AT PACKAGING
    from tap.arg_check              import  arg_check              # REMOVE AT PACKAGING
    from tap.install_package        import  install_package        # REMOVE AT PACKAGING
    from tap.update_package         import  update_package         # REMOVE AT PACKAGING
    from tap.search_package         import  search_package         # REMOVE AT PACKAGING
    from tap.list_packages          import  list_packages          # REMOVE AT PACKAGING

    # Variables we need to function
    application_name = "tap"
    application_version = os.environ.get("TAP_PKGVER", "git")
    mpr_url = "mpr.hunterwittenborn.com"
    os_codename = subprocess.run(["lsb_release", "-cs"],
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True).stdout.strip()

    # Argument check
    argument_list = split_args(sys.argv[1:])
    arg_check_results = arg_check(argument_list, application_name, application_version)

    operation = arg_check_results[0]
    packages = arg_check_results[1]
    argument_options = arg_check_results[2]

    # Run commands
    if operation == "install":
        install_package(mpr_url, packages, "installed", application_name, application_version, os_codename)

    elif operation == "update":
        update_package(mpr_url, application_name, application_version, os_codename)

    elif operation == "search":
        search_package(mpr_url, packages, application_name, application_version, argument_options)

    elif operation == "list-packages":
        list_packages(argument_options)
