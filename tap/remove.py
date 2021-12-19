from tap import cfg
from tap.message import message
from tap.run_transaction import _install_apt_packages
from tap.read_config import get_option

from apt_pkg import (
    CURSTATE_HALF_CONFIGURED,
    CURSTATE_HALF_INSTALLED,
    CURSTATE_INSTALLED,
    CURSTATE_UNPACKED,
)


def remove():
    not_installed = []

    if get_option("remove", "autoremove"):
        for i in cfg.apt_cache.packages:
            if cfg.apt_depcache.is_garbage(i):
                cfg.packages += [i.name]

    for i in cfg.packages:
        try:
            cfg.apt_cache[i]
        except KeyError:
            not_installed += [i]
            continue

        if cfg.apt_cache[i].current_state in (
            CURSTATE_INSTALLED,
            CURSTATE_HALF_INSTALLED,
            CURSTATE_HALF_CONFIGURED,
            CURSTATE_UNPACKED,
        ):
            if get_option("remove", "purge"):
                cfg.apt_depcache.mark_delete(cfg.apt_cache[i], True)
            else:
                cfg.apt_depcache.mark_delete(cfg.apt_cache[i])

            cfg.apt_resolver.protect(cfg.apt_cache[i])
        else:
            not_installed += [i]

        # I (Hunter Wittenborn) can't think of any place where simply removing packages would create any kind of conflicting packages error, though I guess time will tell.
        cfg.apt_resolver.resolve()

    for i in not_installed:
        message.info(f"Package '{i}' isn't installed, so not removing.")

    _install_apt_packages()
