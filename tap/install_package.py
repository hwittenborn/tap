def install_package(**args):
    from shutil import rmtree
    from os.path import exists
    from os import makedirs, chdir
    from tap.get_editor_name import get_editor_name
    from tap.make_mpr_request import make_mpr_request
    from tap.message import message
    from tap.create_mpr_json_dict import create_mpr_json_dict
    from tap.build_dependency_tree import build_dependency_tree
    from tap.clone_packages import clone_packages
    from tap.builddir_del_error import builddir_del_error
    from tap.run_loading_function import run_loading_function

    mpr_url = args["mpr_url"]
    packages = args["packages"]
    application_name = args["application_name"]
    application_version = args["application_version"]
    os_codename = args["os_codename"]
    os_architecture = args["os_architecture"]
    apt_cache = args["apt_cache"]
    builddir = "/var/tmp/tap/"

    # Get editor name.
    editor_name = get_editor_name()

    # Make MPR request.
    json_data = make_mpr_request(packages, mpr_url, application_name, application_version)
    json_data = create_mpr_json_dict(json_data)

    # Make sure all specified packages were able to be found.
    if len(json_data) != len(packages):
        missing_packages = []

        for i in packages:
            if i not in json_data.keys():
                missing_packages += [i]

        message("error", "The following packages couldn't be found:")

        for i in missing_packages:
            message("info2", i)
        exit(1)

    # If old build directory exists, delete it.
    if exists(builddir):
        if rmtree.avoids_symlink_attacks != True:
            message("error", "Old build directory exists, and Tap can't confirm if it can safely delete the build directory.")
            message("error", f"Please check '{builddir}', and delete it yourself if you know it is safe to do so.")
            exit(1)

        info_message = message("info", "Removing old build directory...", value_return=True)
        run_loading_function(info_message, rmtree, builddir, onerror=builddir_del_error)

    # Create the build directory.
    info_message = message("info", "Creating build directory...", value_return=True)
    
    try: run_loading_function(info_message, makedirs, builddir)
    except PermissionError:
        message("error", "Couldn't create the build directory.")
        message("error", f"Make sure the parent directories of '{builddir}' are writable and try again.")
        exit(1)
    
    # Clone packages.
    chdir(builddir)
    info_message = message("info", "Cloning packages...", value_return=True)
    failed_clones = run_loading_function(info_message, clone_packages, packages=packages, mpr_url=mpr_url)
    
    if failed_clones != []:
        message("error", "Some packages failed to clone:")

        for i in failed_clones:
            message("info2", i)

        exit(1)

    # Build dependency tree for packages.
    info_message = message("info", "Building dependency tree...", value_return=True)
    run_loading_function(info_message, build_dependency_tree, packages=packages, os_codename=os_codename, os_architecture=os_architecture)
