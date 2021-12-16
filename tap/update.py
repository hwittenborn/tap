import json

import requests
from tap import cfg
from tap.apt_fetch_packages import apt_fetch_packages
from tap.exceptions import newline_error_exception
from tap.message import message
from tap.run_loading_function import run_loading_function
from tap.list import _list_all_packages
from tap.read_mpr_cache import read_mpr_cache

def _update_apt():
    cfg.apt_cache.update(apt_fetch_packages(), cfg.apt_sourcelist)


def _update_mpr():
    try:
        response = requests.get(f"https://{cfg.mpr_url}/packages-meta-ext-v1.json.gz")
        json.loads(response.text)
        assert response.status_code == 200

    except (requests.exceptions.ConnectionError, AssertionError):
        msg = message.error(
            "Failed to download package cache from MPR.",
            newline=False,
            value_return=True,
        )
        raise newline_error_exception(msg)

    except json.decoder.JSONDecodeError:
        msg = message.error(
            "Error parsing returned package cache from MPR.",
            newline=False,
            value_return=True,
        )
        raise newline_error_exception(msg)
    
    with open(f"/var/cache/{cfg.application_name}/mpr-cache.json", "w") as file:
        file.write(response.text)
    
    cfg.mpr_cache = read_mpr_cache()

def _update_cache_files():
    _list_all_packages()
    
    with open(f"/var/cache/{cfg.application_name}/pkglist", "w") as file:
        for i in cfg.packages: file.write(f"{i}\n")

def update():
    msg = message.info("Updating APT cache...", newline=False, value_return=True)
    run_loading_function(msg, _update_apt)

    msg = message.info("Updating MPR cache...", newline=False, value_return=True)
    run_loading_function(msg, _update_mpr)
    
    msg = message.info("Updating other cache files...", newline=False, value_return=True)
    run_loading_function(msg, _update_cache_files)

    exit(0)
