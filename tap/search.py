import subprocess
from os import get_terminal_size

from tap import cfg
from tap.check_version import check_version
from tap.colors import colors
from tap.message import message
from tap.run_loading_function import run_loading_function
from tap.read_config import get_option


def _get_apt_package_descriptions():
    returned_dict = {}

    for i in cfg.apt_cache.packages:
        # Packages won't have versions if they're a virtual package.
        if not i.has_versions:
            continue

        # apt_pkg.Cache().packages includes packages not available on our architecture, but we don't want those.
        # apt_pkg.Cache().packages also seems to say packages (even ones that aren't available for our architecture) have versions available. We need to check if the apt_pkg.Cache()[pkgname] version has versions available.
        try:
            if not cfg.apt_cache[i.name].has_versions:
                continue
        except KeyError:
            continue

        pkgbase = cfg.apt_depcache.get_candidate_ver(i)

        # 'pkgbase' will be None for any deconfigured packages that don't have any other versions that the deconfigured one available.
        if pkgbase is None:
            continue

        cfg.apt_pkgrecords.lookup(pkgbase.file_list[0])
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

    returned_version = version_list[0]

    for i in version_list:
        if check_version(i, ">", returned_version):
            returned_version = i

    return returned_version


def _get_description(pkgname):
    try:
        cache_pkg = cfg.apt_cache[pkgname]

        # Package won't have any descriptions to pull from if it has no available versions.

        if not cache_pkg.has_versions:
            return None

        cache_version = cfg.apt_depcache.get_candidate_ver(cache_pkg)

        # 'cache_version' will be None for any deconfigured packages that don't have any other versions that the deconfigured one available.
        if cache_version is None:
            return None

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

    if get_option("sort", "rev_alpha"):
        packages.reverse()

    list_length = len(packages) - 1

    for index, pkgname in enumerate(packages):
        if get_option("filter", "pkgname_only"):
            results_string += f"{pkgname}\n"
            continue

        pkgver = _get_latest_version(pkgname)
        pkgdesc = _get_description(pkgname)

        bracketed_strings = []

        if cfg.dpkg_packages.get(pkgname) is not None:
            if cfg.dpkg_packages[pkgname].get("MPR-Package") is None:
                installed_mpr = False
            else:
                installed_mpr = True
        else:
            installed_mpr = None

        if (pkgname in cfg.apt_cache) and (not installed_mpr):
            bracketed_strings += [f"{colors.debian}APT{colors.normal}"]
        if pkgname in cfg.mpr_cache.package_names:
            bracketed_strings += [f"{colors.orange}MPR{colors.normal}"]

        if installed_mpr is False:
            bracketed_strings += [f"{colors.cyan}Installed-APT{colors.normal}"]
        elif installed_mpr is True:
            bracketed_strings += [f"{colors.cyan}Installed-MPR{colors.normal}"]

        if bracketed_strings == []:
            bracketed_text = ""
        else:
            bracketed_text = " [" + ", ".join(bracketed_strings) + "]"

        results_string += (
            f"{colors.apt_green}{pkgname}{colors.normal}/{pkgver}{bracketed_text}\n"
        )

        if pkgdesc is not None:
            results_string += f"  {pkgdesc}\n"

        if index < list_length:
            results_string += "\n"

    return results_string


def _print_results():
    if "--quiet" not in cfg.options:
        msg = message.info("Generating results...", value_return=True, newline=False)
        results = run_loading_function(msg, _generate_results)
    else:
        results = _generate_results()

    if (len(results.splitlines()) > get_terminal_size().lines) and (
        not get_option("output", "skip_less_pipe")
    ):
        subprocess.run(["less", "-r"], input=results.encode())
    else:
        print(results, end="")


def search():
    # Get list of package descriptions for packages in APT cache.
    if not get_option("filter", "mpr_only"):
        if not get_option("output", "quiet"):
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
        if not get_option("filter", "mpr_only"):
            for apt_pkg in apt_package_descriptions:
                if (pkg in apt_pkg) or (pkg in apt_package_descriptions[apt_pkg]):
                    cfg.apt_packages += [apt_pkg]

        if not get_option("filter", "apt_only"):
            # Search MPR packages.
            for mpr_pkg in cfg.mpr_cache.package_dicts:
                pkgdesc = cfg.mpr_cache.package_dicts[mpr_pkg].description
                if pkgdesc is None:
                    pkgdesc = ""

                if (pkg in mpr_pkg) or (pkg in pkgdesc):
                    cfg.mpr_packages += [mpr_pkg]

    # Print results.
    _print_results()
