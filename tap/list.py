from tap import cfg
from tap.search import _print_results
from tap.message import message
from tap.run_loading_function import run_loading_function
from tap.read_config import get_option
from tap.check_version import check_version
from tap.utils import is_installed


def _list_all_packages():
    for i in cfg.apt_cache.packages:
        # apt_pkg.Cache().packages includes packages not available on our architecture, but we don't want those.
        # apt_pkg.Cache().packages also seems to say packages (even ones that aren't available for our architecture) have versions available. We need to check if the apt_pkg.Cache()[pkgname] version has versions available.
        try:
            if not cfg.apt_cache[i.name].has_versions:
                continue
        except KeyError:
            continue

        cfg.packages += [i.name]

    for i in cfg.mpr_cache.package_bases:
        cfg.packages += [i]

    cfg.packages = list(set(cfg.packages))
    cfg.packages.sort()


def _process_packages():
    # Process APT packages.
    for pkg in cfg.packages:
        installed = is_installed(pkg)

        if pkg in cfg.apt_cache:
            if get_option("filter", "installed") and (not installed):
                continue
            # Packages that aren't installed will be reported as upgradable, so we need those package appropriately here (we're not gonna show them).
            if get_option("filter", "upgradable") and (
                not cfg.apt_depcache.is_upgradable(cfg.apt_cache[pkg])
                or installed != "apt"
            ):
                continue
            if get_option("filter", "apt_only") and (installed not in (False, "apt")):
                continue
            if get_option("filter", "mpr_only"):
                continue

            cfg.apt_packages += [pkg]

    # Process MPR packages.
    for pkg in cfg.packages:
        installed = is_installed(pkg)

        if pkg in cfg.mpr_cache.package_names:
            if installed is not False:
                current_version = cfg.apt_cache[pkg].current_ver.ver_str
                latest_version = cfg.mpr_cache.package_dicts[pkg].version
                upgradable = check_version(latest_version, ">", current_version)
            else:
                upgradable = False

            if get_option("filter", "installed") and (not installed):
                continue
            # If a package wasn't installed from the MPR, we don't want to report it's upgradable via versions from the MPR.
            if get_option("filter", "upgradable") and (
                not upgradable or installed != "mpr"
            ):
                continue
            if get_option("filter", "apt_only"):
                continue
            if get_option("filter", "mpr_only") and (installed not in (False, "mpr")):
                continue

            cfg.mpr_packages += [pkg]


def list_pkg():
    if cfg.packages == []:
        if not get_option("output", "quiet"):
            msg = message.info(
                "Fetching package names...", newline=False, value_return=True
            )
            run_loading_function(msg, _list_all_packages)
        else:
            _list_all_packages()

    if not get_option("output", "quiet"):
        msg = message.info("Processing packages...", newline=False, value_return=True)
        run_loading_function(msg, _process_packages)
    else:
        _process_packages()

    _print_results()
