import subprocess
from os import environ
from sys import argv

# Application information.
application_name = "tap"
application_version = application_version = environ.get("TAP_PKGVER", "git")
application_description = "MPR in your pocket"
called_program = argv[0]
mpr_url = "mpr.hunterwittenborn.com"
os_codename = subprocess.run(
    ["lsb_release", "-cs"], stdout=subprocess.PIPE, universal_newlines=True
).stdout.strip()
os_architecture = subprocess.run(
    ["uname", "-m"], stdout=subprocess.PIPE, universal_newlines=True
).stdout.strip()
editor_name = None

# Information on current transaction.
operation = None
packages = []
apt_packages = []
mpr_packages = []
options = []
unknown_options = []
build_user = None

available_commands = {
    "install": "Install packages",
    "update": "Update local repository caches",
    "remove": "Remove installed packages",
    "search": "Search for packages"
}

requires_arguments = ["install", "remove", "search"]
requires_sudo = ["install", "update", "remove"]
requires_apt_cache = ["install", "upgrade", "remove", "search"]
requires_mpr_cache = ["install", "upgrade", "search"]

# Information on commands.
install_options = {}
update_options = {}
remove_options = {}
search_options = {
    "--help": "Bring up this help menu",
    "--rev-alpha": "Sort package results from Z-A instead of A-Z",
    "--skip-less-pipe": "Don't pipe output into 'less' if output is larger than terminal height",
    "--apt-only": "Only show packages available via APT",
    "--mpr-only": "Only show packages available in the MPR"
}

install_shortopts = {}
update_shortopts = {}
remove_shortopts = {}
search_shortopts = {
    "-h": "--help",
    "-L": "--skip-less-pipe",
    "-R": "--rev-alpha"
}

command_options = {
    "install": (install_options, install_shortopts),
    "update": (update_options, update_shortopts),
    "remove": (remove_options, remove_shortopts),
    "search": (search_options, search_shortopts)
}

# Caches used for package installation.
apt_cache = None
apt_depcache = None
apt_resolver = None
apt_pkgman = None
apt_acquire = None
apt_sourcelist = None
apt_pkgrecords = None
mpr_cache = None

# APT exception errors.
APT_BROKEN_PACKAGES = "E:Unable to correct problems, you have held broken packages."

# Miscellaneous data during package downloads and installation.
currently_fetching_packages = []
failed_downloads = []
first_package_downloaded = False

# SRCINFO parser info.
srcinfo_single_keys = ["pkgbase", "pkgver", "pkgrel", "pkgdesc", "url"]
srcinfo_required_keys = ["pkgbase", "pkgname", "pkgver", "arch"]
