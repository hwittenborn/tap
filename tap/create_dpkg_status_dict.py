def create_dpkg_status_dict():
    from apt_pkg import TagFile

    returned_dict = {}

    with TagFile("/var/lib/dpkg/status") as tagfile:
        for section in tagfile:
            current_dict = {}

            for key in section.keys():
                value = section[key]
                current_dict[key] = value

            pkgname = current_dict["Package"]
            returned_dict[pkgname] = current_dict

    return returned_dict
