def update_package(**args):
    import os
    import json
    import requests
    import datetime

    from apt_pkg                  import version_compare, TagFile
    from tap.install_package      import install_package   
    from tap.message              import message           
    from tap.make_mpr_request     import make_mpr_request
    from tap.create_mpr_json_dict import create_mpr_json_dict

    mpr_url = args["mpr_url"]
    application_name = args["application_name"]
    application_version = args["application_version"]
    os_codename = args["os_codename"]
    os_architecture = args["os_architecture"]
    apt_cache = args["apt_cache"]

    # Get list of MPR packages on the user's system.
    mpr_packages = {}

    with TagFile("/var/lib/dpkg/status") as tagfile:

        for section in tagfile:
            try:
                pkgname = section["Package"]
                pkgver = section["Version"]
                mpr_package = section["MPR-Package"]

                package_dict = {"pkgver": pkgver,
                                "mpr_package": mpr_package}

                mpr_packages[pkgname] = package_dict
            
            except KeyError:
                pass

    # If no MPR packages are present, we're not gonna be able to update anything, so we're just gonna abort.
    if len(mpr_packages) == 0:
        message("info", "No updates available.")
        exit(0)


    # Make MPR request.
    mpr_json = make_mpr_request(mpr_packages.keys(), mpr_url, application_name, application_version)
    mpr_json = create_mpr_json_dict(mpr_json)

    # Check which packages need to be updated.
    to_update = []
    unknown_packages = []

    for package in mpr_packages.keys():
        # We'll get a KeyError if the package isn't available on the MPR (such as when a package has been deleted).
        try:
            mpr_json[package]
        except KeyError:
            unknown_packages += [package]
            continue

        local_pkgver = mpr_packages[package]["pkgver"]
        mpr_pkgver = mpr_json[package]["Version"]

        # Positive values mean the first value is higher than the second (and the reverse for negative values, with 0 for the same).
        if version_compare(local_pkgver, mpr_pkgver) < 0:
            to_update += [package]

    # Print a warning for all installed MPR packages that couldn't be found.
    if len(unknown_packages) != 0:
        message("warning", "You currently have some packages installed from the MPR that were unable to be found.")
        message("warning", "This probably means the package has been deleted, and you should make sure the packages listed below weren't deleted for any malicious reason:")

        for i in unknown_packages:
            message("warning2", i)

    # Continue with updating packages if needed.
    if len(to_update) == 0:
        message("info", "No updates available.")
    else:
        install_package(mpr_url=mpr_url,
                        packages=to_update,
                        application_name=application_name,
                        application_version=application_version,
                        os_codename=os_codename,
                        os_architecture=os_architecture,
                        apt_cache=apt_cache)
