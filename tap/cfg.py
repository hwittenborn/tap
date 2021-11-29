import subprocess
from os import environ
from sys import argv

# Application information.
application_name = "tap"
application_version = application_version = environ.get("TAP_PKGVER", "git")
application_description = "MPR in your pocket"
called_program = argv[0]
mpr_url = "mpr.hunterwittenborn.com"
os_codename = subprocess.run(["lsb_release", "-cs"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
os_architecture = subprocess.run(["uname", "-m"], stdout=subprocess.PIPE, universal_newlines=True).stdout.strip()
editor_name = None

# Information on current transaction.
operation = None
apt_packages = []
mpr_packages = []
options = []
unknown_options = []
build_user = None

available_commands = ["install", "update", "upgrade", "remove", "search", "list-packages"]
requires_arguments = ["install", "remove", "search"]
requires_sudo = ["install", "update", "upgrade", "remove"]
requires_apt_cache = ["install", "upgrade", "remove", "search", "list-packages"]

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
