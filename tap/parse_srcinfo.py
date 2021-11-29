from tap.message import message
from tap.exceptions import newline_error_exception
from tap import cfg

class _srcinfo_class:
    def __init__(self, srcinfo_dict):
        # Normal keys.
        self.pkgbase = srcinfo_dict.get("pkgbase")
        self.pkgname = srcinfo_dict.get("pkgname")
        self.pkgver = srcinfo_dict.get("pkgver")
        self.pkgrel = srcinfo_dict.get("pkgrel")
        self.pkgdesc = srcinfo_dict.get("pkgdesc")
        self.arch = srcinfo_dict["arch"]
        self.license = srcinfo_dict.get("license")
        self.depends = srcinfo_dict.get("depends")
        self.makedepends = srcinfo_dict.get("makedepends")
        self.checkdepends = srcinfo_dict.get("checkdepends")
        self.optdepends = srcinfo_dict.get("optdepends")
        self.conflicts = srcinfo_dict.get("conflicts")
        self.breaks = srcinfo_dict.get("breaks")
        self.provides = srcinfo_dict.get("provides")
        self.replaces = srcinfo_dict.get("replaces")
        self.url = srcinfo_dict.get("url")

        # Extras.
        self.version = f"{self.pkgver}-{self.pkgrel}"

def parse_srcinfo(path):
    # Read file.
    try:
        file = open(path, "r")
        data = file.read()
        file.close()

    except FileNotFoundError:
        error_message = message.error(f"Couldn't find '{path}'.", value_return=True)
        raise newline_error_exception(error_message)

    except PermissionError:
        error_message = message.error(f"Insufficient permissions to read '{path}'.", value_return=True)
        raise newline_error_exception(error_message)
    
    # Parse file.
    current_dict = {}

    for i in data.splitlines():
        if i == "": continue
        i = i.lstrip("\t")

        args = i.split(" = ")
        key = args[0]
        
        try:
            value = " = ".join(args[1:])
        except IndexError:
            message.error("Error parsing SRCINFO file under '{path}'.")
            exit(1)
        
        try: current_dict[key] += [value]
        except KeyError: current_dict[key] = [value]

    # Verify data.
    bad_file = False

    for i in cfg.srcinfo_required_keys:
        try:
            current_dict[i]
        except KeyError:
            message.error(f"Missing key '{i}' in SRCINFO file under '{path}'.")
            bad_file = True

    for i in cfg.srcinfo_single_keys:
        try: current_dict[i]
        except KeyError: continue

        if len(current_dict[i]) > 1:
            message.error(f"Duplicate entries found for '{i}' in SRCINFO file under '{path}'.")
            bad_file = True

    if bad_file: exit(1)

    # Parse distro dependencies properly.
    for dependency in ["depends", "makedepends", "checkdepends", "optdepends", "conflicts", "breaks", "provides", "replaces"]:
        for target in [f"{cfg.os_codename}_{dependency}_{cfg.os_architecture}", f"{cfg.os_codename}_{dependency}", f"{dependency}_{cfg.os_architecture}"]:
            if current_dict.get(target) is not None:
                current_dict[dependency] = current_dict[target]
                break

    # Return an object for the SRCINFO data.
    for i in cfg.srcinfo_single_keys:
        try: current_dict[i]
        except KeyError: continue
        current_dict[i] = current_dict[i][0]

    return _srcinfo_class(current_dict)
