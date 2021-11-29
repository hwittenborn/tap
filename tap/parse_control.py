from apt_pkg import TagSection

def _parse_dependencies(string):
    returned_strings = []

    for dep in string.split(", "):
        for bad_character in ("(", ")", " "):
            dep = dep.replace(bad_character, "")

        for restrictor in ("<", ">"):
            if (restrictor + restrictor) in dep:
                dep = dep.replace((restrictor + restrictor), restrictor)

        returned_strings += [dep]

    return returned_strings

class parse_control():
    def __init__(self, data):
        control = TagSection(data)

        self.pkgname = control["Package"]
        self.version = control["Version"]
        self.arch = control["Architecture"]

        try: self.pkgdesc = control["Description"]
        except KeyError: self.pkgdesc = None

        try: self.url = control["Homepage"]
        except KeyError: self.url = None

        try: self.maintainer = control["Maintainer"].split(", ")
        except KeyError: self.maintainer = []

        try: self.predepends = _parse_dependencies(control["Pre-Depends"])
        except KeyError: self.predepends = []

        try: self.depends = _parse_dependencies(control["Depends"])
        except KeyError: self.depends = []

        try: self.recommends = _parse_dependencies(control["Recommends"])
        except KeyError: self.recommends = []

        try: self.suggests = _parse_dependencies(control["Suggests"])
        except KeyError: self.suggests = []

        try: self.conflicts = _parse_dependencies(control["Conflicts"])
        except KeyError: self.conflicts = []

        try: self.breaks = _parse_dependencies(control["Breaks"])
        except KeyError: self.breaks = []

        try: self.provides = _parse_dependencies(control["Provides"])
        except KeyError: self.provides = []

        try: self.replaces = _parse_dependencies(control["Replaces"])
        except KeyError: self.replaces = []
