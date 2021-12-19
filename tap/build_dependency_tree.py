from tap import cfg
from tap.exceptions import newline_error_exception
from tap.message import message
from tap.run_loading_function import run_loading_function

import apt_pkg
from apt_pkg import CURSTATE_CONFIG_FILES, CURSTATE_INSTALLED, CURSTATE_NOT_INSTALLED


def _build_dependency_tree(**kwargs):
    depends = kwargs["depends"]
    conflicts = kwargs["conflicts"]
    breaks = kwargs["breaks"]

    # Remove duplicate dependency listings.
    for i in [depends, conflicts, breaks]:
        i = list(set(i))

    # Check for any missing dependencies.
    missing_deps = []

    for i in depends:
        try:
            cfg.apt_cache[i]
        except KeyError:
            missing_deps += [i]

    if missing_deps != []:
        msg = message.error(
            "The following dependencies were unable to be found:",
            value_return=True,
        )
        for i in missing_deps:
            msg += message.error2(i, value_return=True)
        raise newline_error_exception(msg)

    # Mark packages for installation/removal as needed.
    for i in depends:
        curstate = cfg.apt_cache[i].current_state
        if curstate == CURSTATE_INSTALLED:
            continue

        cfg.apt_depcache.mark_install(cfg.apt_cache[i], True, False)
        cfg.apt_resolver.protect(cfg.apt_cache[i])

    for i in conflicts + breaks:
        try:
            cfg.apt_cache[i]
        except KeyError:
            continue

        curstate = cfg.apt_cache[i].current_state
        if curstate in (CURSTATE_CONFIG_FILES, CURSTATE_NOT_INSTALLED):
            continue

        cfg.apt_depcache.mark_delete(cfg.apt_cache[i])
        cfg.apt_resolver.protect(cfg.apt_cache[i])

    try:
        cfg.apt_resolver.resolve(True)
    except apt_pkg.Error as e:
        exception = e.args[0]

        if exception == cfg.APT_BROKEN_PACKAGES:
            msg = message.error(
                "Unable to properly build dependency tree.", value_return=True
            )
            msg += message.error(
                "This most likely means the packages you requested have conflicting dependencies.",
                value_return=True,
            )
            raise newline_error_exception(msg)
        else:
            raise e


def build_dependency_tree(*args, **kwargs):
    msg = message.info("Building dependency tree...", newline=False, value_return=True)
    run_loading_function(msg, _build_dependency_tree, *args, **kwargs)
