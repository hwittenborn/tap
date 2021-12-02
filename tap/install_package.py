from os import chdir, makedirs, mkdir
from os.path import exists
from shutil import rmtree

from tap import cfg
from tap.builddir_del_error import builddir_del_error
from tap.clone_packages import clone_packages
from tap.get_editor_name import get_editor_name
from tap.message import message
from tap.read_cache import read_cache
from tap.run_loading_function import run_loading_function
from tap.run_transaction import run_transaction
from tap.set_mpr_dependencies import set_mpr_dependencies
from tap.utils import from_mpr, get_user_selection


def _create_build_dirs():
    makedirs(f"/var/tmp/{cfg.application_name}/")
    mkdir(f"/var/tmp/{cfg.application_name}/source_packages/")
    mkdir(f"/var/tmp/{cfg.application_name}/built_packages/")


def install_package():
    get_editor_name()
    cfg.mpr_cache = read_cache()

    # Make sure all specified packages were able to be found.
    missing_packages = []

    for i in cfg.packages:
        available_apt = False
        available_mpr = False

        if i in cfg.apt_cache:
            if not from_mpr(i):
                available_apt = True
            else:
                available_mpr = True

        if i in cfg.mpr_cache.package_bases:
            available_mpr = True

        if (not available_apt) and (not available_mpr):
            missing_packages += [i]

        elif available_apt and not available_mpr:
            cfg.apt_packages += [i]

        elif not available_apt and available_mpr:
            cfg.mpr_packages += [i]

        elif available_apt and available_mpr:
            msg = message.info(
                f"Package '{i}' is available from multiple sources:", value_return=True
            )

            response = get_user_selection(
                msg, [f"APT", f"MPR"], msg2_function=message.info2, multi_option=False
            )

            if response == "APT":
                cfg.apt_packages += [i]
            else:
                cfg.mpr_packages += [i]

    if missing_packages != []:
        message.error("Couldn't find the following packages:")
        for i in missing_packages:
            message.error2(i)
        exit(1)

    # Mark any APT packages for installation.
    for i in cfg.apt_packages:
        cfg.apt_depcache.mark_install(cfg.apt_cache[i])
        cfg.apt_resolver.protect(cfg.apt_cache[i])

    # If old build directory exists (and we need it), delete it.
    if cfg.mpr_packages != []:
        build_dir = f"/var/tmp/{cfg.application_name}"

        if exists(build_dir):
            if not rmtree.avoids_symlink_attacks:
                message.error(
                    "Old build directory exists, and Tap can't confirm if it can safely delete the build directory."
                )
                message.error(
                    f"Please check '{build_dir}', and delete it yourself if you know it is safe to do so."
                )
                exit(1)

            msg = message.info(
                "Removing old build directory...", value_return=True, newline=False
            )
            run_loading_function(msg, rmtree, build_dir, onerror=builddir_del_error)

        # Create the build directory.
        msg = message.info(
            "Creating build directory...", value_return=True, newline=False
        )

        try:
            run_loading_function(msg, _create_build_dirs)
        except PermissionError:
            message.error("Couldn't create the build directory.")
            message.error(
                f"Make sure the parent directories of '{build_dir}' are writable and try again."
            )
            exit(1)

        # Clone packages.
        chdir(build_dir)
        msg = message.info("Cloning packages...", value_return=True, newline=False)
        run_loading_function(msg, clone_packages)

    # Build dependency tree and install packages.
    set_mpr_dependencies()
    run_transaction()
