def search_package(**args):
    import apt
    import apt_pkg
    import requests
    import json
    import os
    import re
    import subprocess

    from  datetime                   import  datetime
    from  tap.colors                 import  colors                
    from  tap.message                import  message               
    from  tap.check_argument_option  import  check_argument_option 
    from  tap.create_package_dict    import  create_package_dict

    mpr_url = args["mpr_url"]
    packages = args["packages"]
    application_name = args["application_name"]
    application_version = args["application_version"]
    argument_options = args["argument_options"]
    apt_cache = args["apt_cache"]

    # Make and verify request to MPR.
    request_arguments = ""

    for i in packages:
        request_arguments += i

    try: mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=search&arg={request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})
    except requests.exceptions.ConnectionError:
        message("error", "Failed to make request to MPR.")
        quit(1)

    try: mpr_rpc_json_data = json.loads(mpr_rpc_request.text)
    except json.decoder.JSONDecodeError:
        message("error", "There was an error processing your request.")
        quit(1)

    if mpr_rpc_json_data["resultcount"] == 0:
        message("info", "No results.")
        quit(0)

    # Check which packages on the user's system were installed from the MPR.
    installed_mpr_packages = []

    with apt_pkg.TagFile("/var/lib/dpkg/status") as tagfile:
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
            pkg_cache = apt_cache[pkgname]

            if pkg_cache.is_installed:
                bracketed_text += ["Installed"]
            if pkg_cache.is_auto_installed:
                bracketed_text += ["Automatic"]
            
            # If the package is installed, check whether it was installed from the MPR or directly via APT.
            if "Installed" in bracketed_text:
                if pkgname in installed_mpr_packages:
                    bracketed_text += ["MPR"]
                else:
                    bracketed_text += ["APT"]

        except KeyError:
            pass

        if bracketed_text != []:
            bracket_string = " [" + ", ".join(bracketed_text) + "]"
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

    if (len(results_string.splitlines()) > os.get_terminal_size().lines) and ("no-less-pipe" not in argument_options):
        subprocess.run(["less", "-r"], input=results_string.encode())
    else:
        print(results_string, end="")
