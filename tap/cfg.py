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
config_file = environ.get("TAP_CONFIG_FILE", "/etc/tap.cfg")
config_data = {}
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
    "upgrade": "Upgrade installed packages",
    "remove": "Remove installed packages",
    "autoremove": "Remove any unneeded packages",
    "search": "Search for packages",
    "list": "List installed packages",
}

requires_arguments = ["install", "remove", "search"]
optional_arguments = ["list"]
requires_sudo = ["install", "update", "upgrade", "remove", "autoremove"]
requires_apt_cache = [
    "install",
    "update",
    "upgrade",
    "remove",
    "autoremove",
    "search",
    "list",
]
requires_mpr_cache = ["install", "upgrade", "search", "list"]

# Information on commands.
install_options = {"--help": "Bring up this help menu"}
update_options = {"--help": "Bring up this help menu"}
upgrade_options = {
    "--apt-only": "Only consider APT packages for upgrades.",
    "--help": "bring up this help menu",
    "--mpr-only": "Only consider MPR packages for upgrades.",
}
remove_options = {
    "--help": "Bring up this help menu",
    "--purge": "Remove configuration files for packages upon removal",
}
autoremove_options = {"--help": "Bring up this help menu"}
search_options = {
    "--apt-only": "Only show packages available via APT",
    "--help": "Bring up this help menu",
    "--mpr-only": "Only show packages available in the MPR",
    "--skip-less-pipe": "Don't pipe output into 'less' if output is larger than terminal height",
    "--pkgname-only": "Only print package names",
    "--quiet": "Hide information messages.",
    "--rev-alpha": "Sort package results from Z-A instead of A-Z",
}
list_options = {
    "--apt-only": "Only show packages available via APT",
    "--help": "Bring up this help menu",
    "--installed": "Only show installed packages",
    "--skip-less-pipe": "Don't pipe output into 'less' if output is larger than terminal height",
    "--mpr-only": "Only show packages available in the MPR",
    "--pkgname-only": "Only print package names",
    "--quiet": "Hide information messages.",
    "--rev-alpha": "Sort package results from Z-A instead of A-Z",
    "--upgradable": "Only show upgradable packages",
}

install_shortopts = {"-h": "--help"}
update_shortopts = {"-h": "--help"}
upgrade_shortopts = {"-h": "--help", "-a": "--apt-only", "-m": "--mpr-only"}
remove_shortopts = {"-h": "--help", "-p": "--purge"}
autoremove_shortopts = {"-h": "--help"}
search_shortopts = {
    "-a": "--apt-only",
    "-m": "--mpr-only",
    "-p": "--pkgname-only",
    "-h": "--help",
    "-L": "--skip-less-pipe",
    "-R": "--rev-alpha",
    "-q": "--quiet",
}
list_shortopts = {
    "-a": "--apt-only",
    "-m": "--mpr-only",
    "-p": "--pkgname-only",
    "-h": "--help",
    "-L": "--skip-less-pipe",
    "-R": "--rev-alpha",
    "-q": "--quiet",
    "-i": "--installed",
    "-u": "--upgradable",
}
command_options = {
    "install": (install_options, install_shortopts),
    "update": (update_options, update_shortopts),
    "upgrade": (upgrade_options, upgrade_shortopts),
    "remove": (remove_options, remove_shortopts),
    "autoremove": (autoremove_options, autoremove_shortopts),
    "search": (search_options, search_shortopts),
    "list": (list_options, list_shortopts),
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
dpkg_packages = None

# APT exception errors.
APT_BROKEN_PACKAGES = "E:Unable to correct problems, you have held broken packages."

# Miscellaneous data during package downloads and installation.
currently_fetching_packages = []
failed_downloads = []
first_package_downloaded = False
loading_function_status = None

# SRCINFO parser info.
srcinfo_single_keys = ["pkgbase", "pkgver", "pkgrel", "pkgdesc", "url"]
srcinfo_required_keys = ["pkgbase", "pkgname", "pkgver", "arch"]
