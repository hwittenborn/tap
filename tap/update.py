import json

import requests
from tap import cfg
from tap.exceptions import newline_error_exception
from tap.message import message
from tap.run_loading_function import run_loading_function


def _update():
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


def update():
    msg = message.info("Updating MPR cache...", newline=False, value_return=True)
    run_loading_function(msg, _update)
    exit(0)
