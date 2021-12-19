from tap import cfg
from tap.check_version import check_version
from tap.get_editor_name import get_editor_name
from tap.install import _run_pre_transaction
from tap.run_loading_function import run_loading_function
from tap.message import message
from tap.read_config import get_option

from apt_pkg import CURSTATE_INSTALLED


def _upgrade():
    for i in cfg.apt_cache.packages:
        if i.current_state != CURSTATE_INSTALLED:
            continue

        if cfg.dpkg_packages[i.name].get("MPR-Package") is not None:
            mpr_package = True
        else:
            mpr_package = False

        if (not mpr_package) and (not get_option("filter", "mpr_only")):
            if cfg.apt_depcache.is_upgradable(i):
                cfg.apt_depcache.mark_install(i)
                cfg.apt_resolver.protect(i)

        elif (mpr_package) and (not get_option("filter", "apt_only")):
            rpc_data = cfg.mpr_cache.package_dicts[i.name]
            current_pkgver = i.current_ver.ver_str
            latest_pkgver = rpc_data.version

            if check_version(latest_pkgver, ">", current_pkgver):
                cfg.mpr_packages += [rpc_data.pkgbase]

    cfg.mpr_packages = list(set(cfg.mpr_packages))


def upgrade():
    get_editor_name()

    msg = message.info("Calculating upgrade...", newline=False, value_return=True)
    run_loading_function(msg, _upgrade)

    _run_pre_transaction()
