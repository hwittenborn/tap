from apt_pkg import TagFile
from tap import cfg


def read_dpkg_status_file():
    cfg.dpkg_packages = {}

    with TagFile("/var/lib/dpkg/status") as file:
        for section in file:
            pkgname = section["Package"]
            cfg.dpkg_packages[pkgname] = section
