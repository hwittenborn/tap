def search_package():
    import apt
    import requests
    import json
    import os
    import re
    import subprocess

    from apt_pkg import TagFile, INSTSTATE_OK
    from datetime import datetime
    from tap.colors import colors
    from tap.message import message
    from tap.check_argument_option import check_argument_option
    from tap import cfg

    # Make and verify request to MPR.
    request_arguments = ""

    for i in cfg.packages:
        request_arguments += i

    try: mpr_rpc_request = requests.get(f"https://{cfg.mpr_url}/rpc/?v=5&type=search&arg={request_arguments}", headers={"User-Agent": f"{cfg.application_name}/{cfg.application_version}"})
    except requests.exceptions.ConnectionError:
        message.error("Failed to make request to MPR.")
        quit(1)

    try: mpr_rpc_json_data = json.loads(mpr_rpc_request.text)
    except json.decoder.JSONDecodeError:
        message.error("There was an error processing your request.")
        quit(1)

    if mpr_rpc_json_data["resultcount"] == 0:
        message.info("No results.")
        quit(0)

    # Check which packages on the user's system were installed from the MPR.
    installed_mpr_packages = []

    with TagFile("/var/lib/dpkg/status") as tagfile:
        for section in tagfile:
            try:
                section["MPR-Package"]
                installed_mpr_packages += [section["Package"]]
            except KeyError:
                pass

    # Generate results.
    result_count = mpr_rpc_json_data["resultcount"]
    number = 1
    results_string = ""

    for i in mpr_rpc_json_data["results"]:
        pkgname = i["Name"]
        pkgver = i["Version"]
        pkgdesc = i["Description"]
        maintainer = i["Maintainer"]
        votes = i["NumVotes"]
        out_of_date = i["OutOfDate"]
        last_modified = i["LastModified"]

        # Check out of date status.
        if out_of_date is None:
            out_of_date = "N/A"
        else:
            out_of_date = datetime.utcfromtimestamp(out_of_date).strftime("%Y-%m-%d")

        # Create last modified date.
        last_modified = datetime.utcfromtimestamp(last_modified).strftime("%Y-%m-%d")

        # Generate bracketed text.
        bracketed_text = []

        try:
            pkg_cache = cfg.apt_cache[pkgname]
            pkg_installed = pkg_cache.inst_state == INSTSTATE_OK
            if pkg_installed:
                bracketed_text += [f"{colors.cyan}Installed{colors.normal}"]
            if cfg.apt_depcache.is_auto_installed(pkg_cache):
                bracketed_text += [f"{colors.magenta}Automatic{colors.normal}"]
            
            # If the package is installed, check whether it was installed from the MPR or directly via APT.
            if pkg_installed:
                if pkgname in installed_mpr_packages:
                    bracketed_text += [f"{colors.orange}MPR{colors.normal}"]
                else:
                    bracketed_text += [f"{colors.orange}APT{colors.normal}"]

        except KeyError:
            pass

        if bracketed_text != []:
            bracket_string = f" [" + ", ".join(bracketed_text) + f"]"
        else:
            bracket_string = ""

        # Actually generate results text.
        results_string += f"{colors.apt_green}{pkgname}{colors.white}/{pkgver}{bracket_string}\n"
        results_string += f"  Description: {pkgdesc}\n"
        results_string += f"  Maintainer: {maintainer}\n"
        results_string += f"  Votes: {votes}\n"
        results_string += f"  Out of Date: {out_of_date}\n"
        results_string += f"  Last Modified: {last_modified}\n"

        if number < result_count:
            results_string += "\n"
        
        number = number + 1

    if (len(results_string.splitlines()) > os.get_terminal_size().lines) and ("--skip-less-pipe" not in cfg.options):
        subprocess.run(["less", "-r"], input=results_string.encode())
    else:
        print(results_string, end="")
