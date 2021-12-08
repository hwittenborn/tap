from tap import cfg
from tap.search import _print_results
from tap.message import message
from tap.run_loading_function import run_loading_function


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
    for pkg in cfg.packages:
        if cfg.dpkg_packages.get(pkg):
            if cfg.dpkg_packages[pkg].get("MPR-Package") is None:
                installed = "apt"
            else:
                installed = "mpr"
        else:
            installed = False

        # Process APT listings.
        if pkg in cfg.apt_cache:
            if ("--installed" in cfg.options) or (cfg.config_data["list"]["installed"]):
                if installed is False:
                    continue
            if ("--upgradable" in cfg.options) or (
                cfg.config_data["list"]["upgradable"]
            ):
                if not cfg.apt_depcache.is_upgradable(cfg.apt_cache[pkg]):
                    continue
            if ("--apt-only" in cfg.options) or (cfg.config_data["list"]["apt_only"]):
                if installed not in (False, "apt"):
                    continue
            if ("--mpr-only" in cfg.options) or (cfg.config_data["list"]["mpr_only"]):
                continue

            cfg.apt_packages += [pkg]

    for pkg in cfg.packages:
        if pkg in cfg.mpr_cache.package_names:
            if ("--installed" in cfg.options) or (cfg.config_data["list"]["installed"]):
                if installed is False:
                    continue
            if ("--upgradable" in cfg.options) or (
                cfg.config_data["list"]["upgradable"]
            ):
                if not cfg.apt_depcache.is_upgradable(cfg.apt_cache[pkg]):
                    continue
            if ("--apt-only" in cfg.options) or (cfg.config_data["list"]["apt_only"]):
                continue
            if ("--mpr-only" in cfg.options) or (cfg.config_data["list"]["mpr_only"]):
                if installed not in (False, "mpr"):
                    continue

            cfg.mpr_packages += [pkg]


def list_pkg():
    if cfg.packages == []:
        if "--quiet" not in cfg.options:
            msg = message.info(
                "Fetching package names...", newline=False, value_return=True
            )
            run_loading_function(msg, _list_all_packages)
        else:
            _list_all_packages()

    if "--quiet" not in cfg.options:
        msg = message.info("Processing packages...", newline=False, value_return=True)
        run_loading_function(msg, _process_packages)
    else:
        _process_packages()

    _print_results()
