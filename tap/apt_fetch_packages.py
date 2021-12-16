from apt.progress.base import AcquireProgress
from tap import cfg
from tap.message import message
from time import sleep

class apt_fetch_packages(AcquireProgress):
    def fetch(self, item):
        if (not cfg.first_package_downloaded) and (cfg.operation != "update"):
            message.info("Downloading needed archives...")
            cfg.first_package_downloaded = True

    def done(self, item):
        if cfg.operation == "update":
            return
        message.info2(f"Finished download of '{item.shortdesc}'.")

    def fail(self, item):
        cfg.failed_downloads += [item.shortdesc]
