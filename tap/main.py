#!/usr/bin/env python3
from tap import cfg
from tap.apt_fetch_packages import apt_fetch_packages
from tap.arg_check import arg_check
from tap.install_package import install_package
from tap.message import message
from tap.remove import remove
from tap.root_check import root_check
from tap.run_loading_function import run_loading_function
from tap.search_package import search_package
from tap.update import update

import apt_pkg


def main():
    arg_check()

    if cfg.operation in cfg.requires_sudo:
        root_check()

    # Generate APT cache if we're going to need it.
    if cfg.operation in cfg.requires_apt_cache:
        apt_pkg.init()

        info_message = message.info(
            "Reading APT cache...", value_return=True, newline=False
        )
        cfg.apt_cache = run_loading_function(info_message, apt_pkg.Cache, None)
        cfg.apt_depcache = apt_pkg.DepCache(cfg.apt_cache)
        cfg.apt_resolver = apt_pkg.ProblemResolver(cfg.apt_depcache)
        cfg.apt_pkgman = apt_pkg.PackageManager(cfg.apt_depcache)
        cfg.apt_acquire = apt_pkg.Acquire(apt_fetch_packages())
        cfg.apt_sourcelist = apt_pkg.SourceList()
        cfg.apt_sourcelist.read_main_list()
        cfg.apt_pkgrecords = apt_pkg.PackageRecords(cfg.apt_cache)

    # Run commands.
    if cfg.operation == "install":
        install_package()
    elif cfg.operation == "update":
        update()
    elif cfg.operation == "remove":
        remove()
    elif cfg.operation == "search":
        search_package()
