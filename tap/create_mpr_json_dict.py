def create_mpr_json_dict(json_data):
    returned_dict = {}

    for i in json_data["results"]:
        pkgname = i["Name"]
        returned_dict[pkgname] = i

    return returned_dict
