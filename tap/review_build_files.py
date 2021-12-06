import subprocess
from os import chdir
from subprocess import PIPE
from time import sleep

from tap import cfg
from tap.message import message


def review_build_files():
    skip_all_build_files = False

    for pkgname in cfg.mpr_packages:
        if skip_all_build_files:
            break
        print()

        while True:
            msg = message.question(
                f"Look over build files for '{pkgname}'? [Y/n/s] ",
                newline=False,
                value_return=True,
            )
            response = input(msg).lower()

            if response == "s":
                message.warning("Skipping build file review for all packages.")
                skip_all_build_files = True
                break

            elif response == "n":
                break

            chdir(f"/var/tmp/{cfg.application_name}/source_packages/{pkgname}/")
            files = ["PKGBUILD"] + subprocess.run(
                [
                    "find",
                    "./",
                    "-type",
                    "f",
                    "-not",
                    "-path",
                    "./PKGBUILD",
                    "-not",
                    "-path",
                    "./.SRCINFO",
                    "-not",
                    "-path",
                    "./.git/*",
                ],
                stdout=PIPE,
            ).stdout.splitlines()

            for file in files:
                exit_code = subprocess.run([cfg.editor_name, "--", file]).returncode

                if exit_code != 0:
                    message.error(
                        f"Command '{cfg.editor_name} -- {file}' didn't finish succesfully."
                    )
                    exit(0)

            sleep(0.5)
