import subprocess
from concurrent.futures import ThreadPoolExecutor
from os import chdir
from subprocess import DEVNULL, PIPE

from tap import cfg
from tap.exceptions import newline_error_exception
from tap.message import message


def clone_packages():
    chdir(f"/var/tmp/{cfg.application_name}/source_packages/")

    with ThreadPoolExecutor() as executor:
        package_threads = {}

        for i in cfg.mpr_packages:
            package_threads[i] = executor.submit(
                subprocess.run,
                ["git", "clone", "--", f"https://{cfg.mpr_url}/{i}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        running_threads = True

        while running_threads:
            running_threads = False

            for i in cfg.mpr_packages:
                if package_threads[i].running():
                    running_threads = True

    failed_clones = []

    for i in cfg.mpr_packages:
        if package_threads[i].result().returncode != 0:
            failed_clones += [i]

    if failed_clones != []:
        msg = message.error(
            "Failed to clone the following MPR packages:", value_return=True
        )

        for i in failed_clones:
            msg += message.error2(i, value_return=True)
        raise newline_error_exception(msg)

    for i in cfg.mpr_packages:
        proc = subprocess.run(
            ["chown", "-Rh", f"{cfg.build_user}", "--", i], stdout=DEVNULL, stderr=PIPE
        )

        if proc.returncode != 0:
            msg = proc.stderr.decode().strip() + "\n"
            msg += message.error(
                f"Failed to set permissions on cloned repository for '{i}'.",
                value_return=True,
            )
            raise newline_error_exception(msg)
