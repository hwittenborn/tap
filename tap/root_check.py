import sys
import subprocess
from os import environ

from tap import cfg
from tap.message import message


def root_check():
    sudo_uid = environ.get("SUDO_UID")

    if sudo_uid is None:
        message.error(
            "Tap needs to run under sudo(8) in order to modify packages on your system."
        )
        message.error("Please run Tap under sudo(8) and try again.")
        sys.exit(1)

    command = subprocess.run(
        ["sudo", "-nu", f"#{sudo_uid}", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if command.returncode != 0:
        message.error(f"Couldn't obtain permissions to run under UID '{sudo_uid}'.")
        sys.exit(1)

    cfg.build_user = sudo_uid
