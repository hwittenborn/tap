import sys
import subprocess

from shutil import rmtree
from subprocess import DEVNULL, PIPE
from os.path import exists
from os import makedirs, mkdir, chdir
from time import sleep
from tempfile import NamedTemporaryFile
from tap.get_editor_name import get_editor_name
from tap.make_mpr_request import make_mpr_request
from tap.message import message
from tap.create_mpr_json_dict import create_mpr_json_dict
from tap.clone_packages import clone_packages
from tap.builddir_del_error import builddir_del_error
from tap.run_loading_function import run_loading_function
from tap.colors import colors
from tap.apt_fetch_packages import apt_fetch_packages
from tap.apt_install_packages import apt_install_packages
from tap import cfg
from tap.read_cache import read_cache
from tap.run_transaction import run_transaction
from tap.set_mpr_dependencies import set_mpr_dependencies

def _create_build_dirs():
    makedirs(f"/var/tmp/{cfg.application_name}/")
    mkdir(f"/var/tmp/{cfg.application_name}/source_packages/")
    mkdir(f"/var/tmp/{cfg.application_name}/built_packages/")

def install_package():
    get_editor_name()
    cfg.mpr_cache = read_cache()

    # Make sure all specified packages were able to be found.
    missing_packages = []

    for i in cfg.mpr_packages:
        if i not in cfg.mpr_cache.package_bases:
            missing_packages += [i]

    if missing_packages != []:
        message.error("Couldn't find the following packages:")
        for i in missing_packages: message.error2(i)
        exit(1)

    # If old build directory exists, delete it.
    build_dir = f"/var/tmp/{cfg.application_name}"
    
    if exists(build_dir):
        if rmtree.avoids_symlink_attacks != True:
            message.error("Old build directory exists, and Tap can't confirm if it can safely delete the build directory.")
            message.error(f"Please check '{build_dir}', and delete it yourself if you know it is safe to do so.")
            exit(1)

        msg = message.info("Removing old build directory...", value_return=True, newline=False)
        run_loading_function(msg, rmtree, build_dir, onerror=builddir_del_error)

    # Create the build directory.
    msg = message.info("Creating build directory...", value_return=True, newline=False)
    
    try: run_loading_function(msg, _create_build_dirs)
    except PermissionError:
        message.error("Couldn't create the build directory.")
        message.error(f"Make sure the parent directories of '{build_dir}' are writable and try again.")
        exit(1)
    
    # Clone packages.
    chdir(build_dir)
    msg = message.info("Cloning packages...", value_return=True, newline=False)
    run_loading_function(msg, clone_packages)
    
    # Build dependency tree and install packages.
    set_mpr_dependencies()
    run_transaction()