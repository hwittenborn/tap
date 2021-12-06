import json
from os.path import exists

from tap import cfg
from tap.message import message
from tap.exceptions import newline_error_exception

class _create_pkg_object:
    def __init__(self, json_dict):
        self.pkgbase = json_dict["PackageBase"]
        self.pkgname = json_dict["Name"]
        self.version = json_dict["Version"]
        self.description = json_dict["Description"]
        self.numvotes = json_dict["NumVotes"]
        self.popularity = json_dict["Popularity"]
        self.outofdate = json_dict["OutOfDate"]
        self.maintainer = json_dict["Maintainer"]
        self.firstsubmitted = json_dict["FirstSubmitted"]
        self.lsatmodified = json_dict["LastModified"]
        self.urlpath = json_dict["URLPath"]
        self.license = json_dict.get("License", [])
        self.keywords = json_dict.get("Keywords", [])


class read_mpr_cache:
    def __init__(self):
        filename = f"/var/cache/{cfg.application_name}/mpr-cache.json"

        if not exists(filename):
            msg = message.error("Repository cache for the MPR doesn't currently exist.", value_return=True)
            msg += message.error(f"Run 'sudo {cfg.application_name} update' and try again.", value_return=True)
            raise newline_error_exception(msg)

        with open(filename, "r") as file:
            data = file.read()

        if data.strip() == "":
            msg = message.error("Repository cache for the MPR is empty.", value_return=True)
            msg += message.error(f"Run 'sudo {cfg.application_name} update' and try again.", value_return=True)
            raise newline_error_exception(msg)

        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            msg = message.error("Error parsing MPR repository cache.", value_return=True)
            msg += message.error(f"Run 'sudo {cfg.application_name} update' and try again.", value_return=True)
            raise newline_error_exception(msg)

        self.package_bases = []
        self.package_names = []
        self.package_dicts = {}

        for i in data:
            pkgbase = i["PackageBase"]
            pkgname = i["Name"]

            self.package_bases += [pkgbase]
            self.package_names += [pkgname]
            self.package_dicts[pkgname] = _create_pkg_object(i)
