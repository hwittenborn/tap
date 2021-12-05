import subprocess
from os import chdir
from shutil import copy2
from subprocess import PIPE

from apt.debfile import DebPackage
from tap import cfg
from tap.build_dependency_tree import build_dependency_tree
from tap.colors import colors
from tap.generate_apt_styled_text import generate_apt_styled_text
from tap.message import message
from tap.parse_control import parse_control
from tap.parse_srcinfo import parse_srcinfo
from tap.review_build_files import review_build_files


def _install_apt_packages(**kwargs):
    show_to_build = kwargs.get("show_to_build", True)

    to_apt_install = []
    to_additionally_install = []
    to_upgrade = []
    to_downgrade = []
    to_remove = []
    to_remove_essential = []

    for i in cfg.apt_cache.packages:
        if cfg.apt_depcache.marked_install(i):
            to_apt_install += [i.name]

            if i.name not in (cfg.apt_packages + cfg.mpr_packages):
                to_additionally_install += [i.name]

        elif cfg.apt_depcache.marked_upgrade(i):
            to_upgrade += [i.name]

        elif cfg.apt_depcache.marked_downgrade(i):
            to_downgrade += [i.name]

        elif cfg.apt_depcache.marked_delete(i):
            to_remove += [i.name]
            if i.essential:
                to_remove_essential += [i.name]

    for i in [to_apt_install, to_upgrade, to_downgrade, to_remove]:
        i.sort()

    # Abort transaction if we would remove essential packages in the process.
    # TODO: Allow this to happen, albeit by many alerting prompts to make sure the user really wants to do it.
    if to_remove_essential != []:
        message.error(
            "Refusing to complete transaction, as the following essential packages would be removed:"
        )
        for i in to_remove_essential:
            message.error2(i)
        exit(1)

    print(colors.bold)
    if show_to_build:
        generate_apt_styled_text(
            "The following packages are going to be built:", cfg.mpr_packages
        )

    generate_apt_styled_text(
        "The following packages are going to be installed:",
        cfg.mpr_packages + to_apt_install,
    )
    generate_apt_styled_text(
        "The following additional packages are going to be installed:",
        to_additionally_install,
    )
    generate_apt_styled_text(
        "The following packages are going to be upgraded:", to_upgrade
    )
    generate_apt_styled_text(
        "The following packages are going to be DOWNGRADED:", to_downgrade
    )
    generate_apt_styled_text(
        "The following packages are going to be REMOVED:", to_remove
    )

    len_to_install = len(cfg.mpr_packages + to_apt_install)
    len_to_upgrade = len(to_upgrade)
    len_to_downgrade = len(to_downgrade)
    len_to_remove = len(to_remove)

    print(
        f"{len_to_install} to install, {len_to_upgrade} to upgrade, {len_to_downgrade} to downgrade, and {len_to_remove} to remove."
    )
    print(f"{colors.normal}", end="")

    if (len_to_install + len_to_upgrade + len_to_downgrade + len_to_remove) == 0:
        exit(0)

    print()
    msg = message.question(
        "Would you like to continue? [Y/n] ", value_return=True, newline=False
    )
    response = input(msg).lower()

    if response not in ("", "y"):
        exit(1)

    # Prompt the user to review build files.
    if show_to_build:
        review_build_files()
        print()

    # Download and install archives.
    if (
        (to_apt_install != [])
        or (to_upgrade != [])
        or (to_downgrade != [])
        or (to_remove != [])
    ):
        cfg.apt_pkgman.get_archives(
            cfg.apt_acquire, cfg.apt_sourcelist, cfg.apt_pkgrecords
        )
        cfg.apt_acquire.run()

        if cfg.failed_downloads != []:
            pass
            message.error("Some packages failed to download:")
            for i in cfg.failed_downloads:
                message.error2(i)

        message.info("Setting up APT packages...")
        with open("/dev/null", "w") as file:
            result = cfg.apt_pkgman.do_install(file.fileno())

        if result == cfg.apt_pkgman.RESULT_FAILED:
            message.error("Failed installing packages.")
            exit(1)


def run_transaction():
    _install_apt_packages()

    if cfg.mpr_packages != []:
        # Start building packages.
        message.info("Building packages...")
        failed_builds = []
        built_packages = []

        for pkgbase in cfg.mpr_packages:
            chdir(f"/var/tmp/{cfg.application_name}/source_packages/{pkgbase}/")

            pkginfo = parse_srcinfo(".SRCINFO")
            pkgname = pkginfo.pkgname
            version = pkginfo.version
            arch = pkginfo.arch
            mpr_package_field = False

            # We have to check for the 'MPR-Package' control field by sourcing the PKGBUILD right now, as makedeb doesn't currently export that field into SRCINFO files.
            control_fields = (
                subprocess.run(
                    [
                        "bash",
                        "-c",
                        "source PKGBUILD; printf '%s' \"${control_fields[@]}\"",
                    ],
                    stdout=PIPE,
                )
                .stdout.decode()
                .splitlines()
            )

            if control_fields != []:
                for field in control_fields:
                    args = field.split(": ")

                    if args[0] == "MPR-Package":
                        mpr_package_field = True
                        break

            # Actually build the package.
            additional_args = []

            if not mpr_package_field:
                additional_args = ["-H", f"MPR-Package: {pkgbase}"]

            proc = subprocess.run(
                ["sudo", "-nu", f"#{cfg.build_user}", "--", "makedeb"] + additional_args
            )

            if proc.returncode != 0:
                message.error(f"Package '{pkgbase}' failed to build.")
                msg = message.question(
                    "Would you like to abort the build process? "
                    "This will result in all packages marked for building not being installed. [Y/n] ",
                    newline=False,
                    value_return=True,
                )

                response = input(msg).lower()

                if response != "n":
                    message.error("Aborting...")
                    exit(1)

                else:
                    message.info("Continuing with builds...")

            # Copy built packages to temp directory for installation later.
            for name in pkgname:
                with open(f"./pkg/{name}/DEBIAN/control", "r") as file:
                    control_info = parse_control(file.read())
                    version = control_info.version
                    arch = control_info.arch

                filename = f"{name}_{version}_{arch}.deb"
                built_packages += [filename]
                copy2(
                    f"./{filename}",
                    f"/var/tmp/{cfg.application_name}/built_packages/{filename}",
                )

        # Install all the packages!
        message.info("Installing built packages...")
        depends_list = []
        conflicts_list = []
        breaks_list = []

        chdir(f"/var/tmp/{cfg.application_name}/built_packages/")

        for i in built_packages:
            debfile = DebPackage(f"./{i}")
            control = debfile.control_content("control")

            control_info = parse_control(control)
            depends_list += control_info.predepends + control_info.depends
            conflicts_list += control_info.conflicts
            breaks_list += control_info.breaks

        build_dependency_tree(
            depends=depends_list, conflicts=conflicts_list, breaks=breaks_list
        )
        _install_apt_packages(show_to_build=False)

        for i in built_packages:
            debfile = DebPackage(f"./{i}")
            debfile.install()

    message.info("Done.")
