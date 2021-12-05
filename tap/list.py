from tap import cfg
from tap.search import _generate_results
from tap.utils import is_installed

def list():
    for pkg in cfg.packages:
        # Process APT listings.
        if pkg in cfg.apt_cache:
            installed = is_installed(pkg)

            if ("--installed" in cfg.options) or (cfg.config_data["list"]["installed"]):
                if installed is False: continue
            if ("--upgradable" in cfg.options) or (cfg.config_data["list"]["upgradable"]):
                if not cfg.apt_depcache.is_upgradable(cfg.apt_cache[pkg]): continue
            if ("--apt-only" in cfg.options) or (cfg.config_data["list"]["apt_only"]):
                if installed not in (False, "apt"): continue
            if ("--mpr-only" in cfg.options) or (cfg.config_data["list"]["mpr_only"]): continue

            cfg.apt_packages += [pkg]

    for pkg in cfg.packages:
        if pkg in cfg.mpr_cache.package_names:
            installed = is_installed(pkg)

            if ("--installed" in cfg.options) or (cfg.config_data["list"]["installed"]):
                if installed is False: continue
            if ("--upgradable" in cfg.options) or (cfg.config_data["list"]["upgradable"]):
                if not cfg.apt_depcache.is_upgradable(cfg.apt_cache[pkg]): continue
            if ("--apt-only" in cfg.options) or (cfg.config_data["list"]["apt_only"]): continue
            if ("--mpr-only" in cfg.options) or (cfg.config_data["list"]["mpr_only"]):
                if installed not in (False, "mpr"): continue

            cfg.mpr_packages += [pkg]
    
    _generate_results()
