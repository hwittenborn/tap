import os

from apt.progress.base import AcquireProgress
from tap.message import message
from tap import cfg

class apt_fetch_packages(AcquireProgress):
    def fetch(self, item):
        if not cfg.first_package_downloaded:
            message.info("Downloading needed archives...")
            cfg.first_package_downloaded = True

    def done(self, item):
        message.info2(f"Finished download of '{item.shortdesc}'.")
    
    def fail(self, item):
        cfg.failed_downloads += [item.shortdesc]
