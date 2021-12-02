#!/usr/bin/env python3
import os

from tap.main import main

os.environ["TAP_PKGVER"] = os.environ.get("TAP_PKGVER", "{pkgver}")

main()
