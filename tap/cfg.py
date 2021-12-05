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
    "list": "List installed packages"
}

requires_arguments = ["install", "remove", "search"]
optional_arguments = ["list"]
requires_sudo = ["install", "update", "upgrade", "remove", "autoremove"]
requires_apt_cache = ["install", "update", "upgrade", "remove", "autoremove", "search", "list"]
requires_mpr_cache = ["install", "upgrade", "search", "list"]

# Information on commands.
install_options = {"--help": "Bring up this help menu"}
update_options = {"--help": "Bring up this help menu"}
upgrade_options = {"--help": "bring up this help menu"}
remove_options = {
    "--help": "Bring up this help menu",
    "--purge": "Remove configuration files for packages upon removal",
}
autoremove_options = {"--help": "Bring up this help menu"}
search_options = {
    "--help": "Bring up this help menu",
    "--rev-alpha": "Sort package results from Z-A instead of A-Z",
    "--skip-less-pipe": "Don't pipe output into 'less' if output is larger than terminal height",
    "--quiet": "Hide information messages.",
    "--apt-only": "Only show packages available via APT",
    "--mpr-only": "Only show packages available in the MPR",
    "--pkgname-only": "Only print package names"
}
list_options = {
    "--help": "Bring up this help menu",
    "--rev-alpha": "Sort package results from Z-A instead of A-Z",
    "--skip-less-pipe": "Don't pipe output into 'less' if output is larger than terminal height",
    "--quiet": "Hide information messages.",
    "--installed": "Only show installed packages",
    "--upgradable": "Only show upgradable packages",
    "--apt-only": "Only show packages available via APT",
    "--mpr-only": "Only show packages available in the MPR",
    "--pkgname-only": "Only print package names"
}

install_shortopts = {"-h": "--help"}
update_shortopts = {"-h": "--help"}
upgrade_shortopts = {"-h": "--help"}
remove_shortopts = {"-h": "--help"}
autoremove_shortopts = {"-h": "--help"}
search_shortopts = {"-h": "--help", "-L": "--skip-less-pipe", "-R": "--rev-alpha", "-q": "--quiet"}
list_shortopts = {"-h": "--help", "-L": "--skip-less-pipe", "-R": "--rev-alpha", "-q": "--quiet"}
command_options = {
    "install": (install_options, install_shortopts),
    "update": (update_options, update_shortopts),
    "upgrade": (upgrade_options, upgrade_shortopts),
    "remove": (remove_options, remove_shortopts),
    "autoremove": (autoremove_options, autoremove_shortopts),
    "search": (search_options, search_shortopts),
    "list": (list_options, list_shortopts)
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
loading_function_status = None

# SRCINFO parser info.
srcinfo_single_keys = ["pkgbase", "pkgver", "pkgrel", "pkgdesc", "url"]
srcinfo_required_keys = ["pkgbase", "pkgname", "pkgver", "arch"]
