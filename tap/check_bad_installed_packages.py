def check_bad_installed_packages(**args):
    from apt_pkg import CURSTATE_INSTALLED, CURSTATE_NOT_INSTALLED, CURSTATE_HALF_INSTALLED, CURSTATE_HALF_CONFIGURED, CURSTATE_UNPACKED, CURSTATE_CONFIG_FILES
    from tap.message import message

    apt_cache = args["apt_cache"]

    packages = apt_cache.packages
    package_count = apt_cache.package_count

    unpacked_packages = []
    currently_installing_packages = []

    # Get states of packages.
    for i in range(package_count):
        current_package = packages[i]
        pkgname = current_package.name
        current_state = current_package.current_state

        if current_state in [CURSTATE_INSTALLED, CURSTATE_NOT_INSTALLED, CURSTATE_CONFIG_FILES]:
            continue
        elif current_state == CURSTATE_UNPACKED:
            unpacked_packages += [pkgname]
        else:
            continue

    # Process states.
    if len(unpacked_packages) != 0:
        message("error", "The following packages haven't been configured on your system:")

        for i in unpacked_packages:
            message("error2", i)

        message("error", "Please run 'sudo tap fix-broken' first, then try again.")
        exit(1)
