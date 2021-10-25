def get_srcinfo_data(**args):
    import re
    from tap.message import message
    from tap.exceptions import newline_error_exception
    
    path = args["path"]
    os_codename = args["os_codename"]
    os_architecture = args["os_architecture"]

    # Read file.
    try:
        with open(path, "r") as file:
            data = file.read()

    except FileNotFoundError:
        error_message = message("error", f"Couldn't find '{path}'.", value_return=True)
        raise newline_error_exception(error_message)

    except PermissionError:
        error_message = message("error", f"Insufficient permissions to read '{path}'.", value_return=True)
        raise newline_error_exception(error_message)

    # Initialize dictionary and dependency lists.
    returned_dict = {}
    dependency_keys = ["depends", "makedepends", "checkdepends", "optdepends", "provides", "breaks", "replaces"]

    for i in dependency_keys:
        returned_dict[i] = []
    
    # Parse data from SRCINFO file.
    for i in data.splitlines():
        if i == "":
            continue
        
        if re.search("^\t", i) is not None:
            current_line = re.sub("^\t", "", i)
        else:
            current_line = i

        current_line = current_line.split(" = ")

        try:
            assert len(current_line) > 1
        except AssertionError:
            error_message = message("error", f"Error parsing '{path}'.", value_return=True)
            raise newline_error_exception(error_message)

        key = current_line[0]
        value = " = ".join(current_line[1:])

        # NameError occurs when we haven't declared the specified type in the srcinfo_data dict yet.
        try:
            returned_dict[key] += [value]
        except KeyError: returned_dict[key] = [value]

    # Order of specificity for dependencies in makedeb is 'codename_depends_arch', 'codename_depends', 'depends_arch', 'depends' (replacing 'depends' with the relevant dependency type).
    for dependency in dependency_keys:
        for targeted_dependency in [dependency, f"{dependency}_{os_architecture}", f"{os_codename}_{dependency}", f"{os_codename}_{dependency}_{os_architecture}"]:
            if returned_dict.get(targeted_dependency) is not None:
                returned_dict[f"{dependency}_key"] = targeted_dependency

    return returned_dict
