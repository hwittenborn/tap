def list_packages(**args):
    import os
    import subprocess

    from tap.colors import colors
    from apt_pkg import TagFile
    from tap.message import message
    from tap.create_dpkg_status_dict import create_dpkg_status_dict

    argument_options = args["argument_options"]
    apt_cache = args["apt_cache"]

    mpr_packages = []
    installed_packages = create_dpkg_status_dict()

    for i in installed_packages.keys():
        current_dict = installed_packages[i]

        if current_dict.get("MPR-Package") is not None:
            mpr_packages += [current_dict["Package"]]

    if mpr_packages == []:
        message("info", "No MPR packages currently installed.")
        exit(0)

    mpr_packages.sort()

    if "--rev-alpha" in argument_options:
        mpr_packages.reverse()

    results_string = ""

    num_mpr_packages = len(mpr_packages) - 1
    number = 0

    for i in mpr_packages:
        current_dict = installed_packages[i]

        pkgbase = current_dict["MPR-Package"]
        pkgname = current_dict["Package"]
        pkgver = current_dict["Version"]
        pkgdesc = current_dict.get("Description", "N/A")
        maintainer = current_dict.get("Maintainer", "N/A")

        results_string += f"{colors.apt_green}{pkgname}{colors.normal}/{pkgver}\n"
        results_string += f"From: {pkgbase}\n"
        results_string += f"Description: {pkgdesc}\n"
        results_string += f"Maintainer: {maintainer}\n"

        if number < num_mpr_packages:
            results_string += "\n"

        number = number + 1
    if (len(results_string.splitlines()) > os.get_terminal_size().lines) and ("no-less-pipe" not in argument_options):
        subprocess.run(["less", "-r"], input=results_string.encode())
    else:
        print(results_string, end="")
