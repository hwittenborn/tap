import subprocess
from os import get_terminal_size

from tap import cfg
from tap.check_version import check_version
from tap.colors import colors
from tap.message import message
from tap.run_loading_function import run_loading_function
from tap.utils import is_installed


def _get_apt_package_descriptions():
    returned_dict = {}

    for i in cfg.apt_cache.packages:
        # Packages won't have versions if they're a virtual package.
        if not i.has_versions:
            continue

        # apt_pkg.Cache().packages includes packages not available on our architecture, but we don't want those.
        try:
            cfg.apt_cache[i.name]
        except KeyError:
            continue

        pkgbase = cfg.apt_depcache.get_candidate_ver(i)

        try:
            cfg.apt_pkgrecords.lookup(pkgbase.file_list[0])
        except AttributeError:
            cfg.apt_cache[i.name]
            exit()

        pkgname = i.name
        pkgdesc = cfg.apt_pkgrecords.short_desc

        returned_dict[pkgname] = pkgdesc

    return returned_dict


def _get_latest_version(pkgname):
    version_list = []

    # Key error will be raised for any package not in the APT cache (i.e. any package from the MPR not available as a native APT package).
    try:
        for i in cfg.apt_cache[pkgname].version_list:
            version_list += [i.ver_str]
    except KeyError:
        pass

    if pkgname in cfg.mpr_cache.package_bases:
        version_list += [cfg.mpr_cache.package_dicts[pkgname].version]

    try:
        returned_version = version_list[0]
    except IndexError:
        print(pkgname)
        exit(1)

    for i in version_list:
        if check_version(i, ">", returned_version):
            returned_version = i

    return returned_version


def _get_description(pkgname):
    try:
        cache_version = cfg.apt_depcache.get_candidate_ver(cfg.apt_cache[pkgname])
        cfg.apt_pkgrecords.lookup(cache_version.file_list[0])
        return cfg.apt_pkgrecords.short_desc
    except KeyError:
        if pkgname not in cfg.mpr_cache.package_names:
            return None
        return cfg.mpr_cache.package_dicts[pkgname].description


def _generate_results():
    results_string = ""
    packages = set(cfg.apt_packages + cfg.mpr_packages)
    packages = list(packages)
    packages.sort()

    if ("--rev-alpha" in cfg.options) or (cfg.config_data["search"]["rev_alpha"]):
        packages.reverse()

    list_length = len(packages) - 1

    for index, pkgname in enumerate(packages):
        if ("--pkgname-only" in cfg.options) or (
            cfg.config_data[cfg.operation]["pkgname_only"]
        ):
            results_string += f"{pkgname}\n"
            continue

        pkgver = _get_latest_version(pkgname)
        pkgdesc = _get_description(pkgname)

        bracketed_strings = []

        installed = is_installed(pkgname)

        if (pkgname in cfg.apt_cache) and (installed != "mpr"):
            bracketed_strings += [f"{colors.debian}APT{colors.normal}"]
        if pkgname in cfg.mpr_cache.package_names:
            bracketed_strings += [f"{colors.orange}MPR{colors.normal}"]

        if installed == "apt":
            bracketed_strings += [f"{colors.cyan}Installed-APT{colors.normal}"]
        elif installed == "mpr":
            bracketed_strings += [f"{colors.cyan}Installed-MPR{colors.normal}"]

        if bracketed_strings == []:
            bracketed_text = ""
        else:
            bracketed_text = " [" + ", ".join(bracketed_strings) + "]"

        results_string += (
            f"{colors.apt_green}{pkgname}{colors.normal}/{pkgver}{bracketed_text}\n"
        )
        results_string += f"  {pkgdesc}\n"

        if index < list_length:
            results_string += "\n"

    if (len(results_string.splitlines()) > get_terminal_size().lines) and (
        "--skip-less-pipe" not in cfg.options
    ):
        subprocess.run(["less", "-r"], input=results_string.encode())
    else:
        print(results_string, end="")


def search():
    # Get list of package descriptions for packages in APT cache.
    if ("--mpr-only" not in cfg.options) and (
        not cfg.config_data["search"]["mpr_only"]
    ):
        if ("--pkgname-only" not in cfg.options) and (
            not cfg.config_data[cfg.operation]["pkgname_only"]
        ):
            msg = message.info(
                "Reading package descriptions...",
                newline=False,
                value_return=True,
            )
            apt_package_descriptions = run_loading_function(
                msg, _get_apt_package_descriptions
            )
        else:
            apt_package_descriptions = _get_apt_package_descriptions()

    # Search each provided package.
    for pkg in cfg.packages:
        if ("--mpr-only" not in cfg.options) and (
            not cfg.config_data["search"]["mpr_only"]
        ):
            for apt_pkg in apt_package_descriptions:
                if (pkg in apt_pkg) or (pkg in apt_package_descriptions[apt_pkg]):
                    cfg.apt_packages += [apt_pkg]

        if ("--apt-only" not in cfg.options) and (
            not cfg.config_data["search"]["apt_only"]
        ):
            # Search MPR packages.
            for mpr_pkg in cfg.mpr_cache.package_dicts:
                pkgdesc = cfg.mpr_cache.package_dicts[mpr_pkg].description
                if pkgdesc is None:
                    pkgdesc = ""

                if (pkg in mpr_pkg) or (pkg in pkgdesc):
                    cfg.mpr_packages += [mpr_pkg]

    # Generate results.
    _generate_results()
