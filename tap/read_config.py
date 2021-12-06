import configparser
from os.path import exists

from tap import cfg
from tap.message import message

_required_keys = ["remove", "search"]
_remove_keys = ["purge"]
_search_keys = ["rev_alpha", "skip_less_pipe", "apt_only", "mpr_only"]

_key_maps = {"remove": _remove_keys, "search": _search_keys}

_default_config = {
    "remove": {"purge": 0},
    "search": {
        "rev_alpha": 0,
        "skip_less_pipe": 0,
        "apt_only": 0,
        "mpr_only": 0,
        "pkgname_only": 0,
    },
    "list": {
        "rev_alpha": 0,
        "skip_less_pipe": 0,
        "installed": 0,
        "upgradable": 0,
        "apt_only": 0,
        "mpr_only": 0,
        "pkgname_only": 0,
    },
}


def read_config():
    config = configparser.ConfigParser()

    if not exists(cfg.config_file):
        if "--quiet" not in cfg.options:
            message.warning(
                "Couldn't find config file, falling back to default values."
            )

        cfg.config_data = _default_config
        return

    config.read(cfg.config_file)
    config_dict = {}

    for item in config.sections():
        current_dict = {}

        for key in config[item]:
            current_dict[key] = config[item][key]

        config_dict[item] = current_dict

    cfg.config_data = config_dict

    # Validate config.
    bad_config_reasons = []

    for item in _required_keys:
        if item not in config_dict:
            msg = message.warning2(
                f"Missing toplevel item '{item}'.", value_return=True
            )
            bad_config_reasons += [msg]
            cfg.config_data[item] = _default_config[item]

    for item in _required_keys:
        for key in _key_maps[item]:
            if key not in config_dict[item]:
                msg = message.warning2(
                    f"Missing key '{key}' under toplevel item '{item}'.",
                    value_return=True,
                )
                bad_config_reasons += [msg]
                cfg.config_data[item][key] = _default_config[item][key]

            else:
                try:
                    cfg.config_data[item][key] = int(cfg.config_data[item][key])
                    assert cfg.config_data[item][key] in (0, 1)

                except (ValueError, AssertionError):
                    msg = message.warning2(
                        f"Invalid value for '{key}' under toplevel item '{item}'.",
                        value_return=True,
                    )
                    bad_config_reasons += [msg]
                    cfg.config_data[item][key] = _default_config[item][key]

    if (bad_config_reasons != []) and ("--quiet" not in cfg.options):
        message.warning("Config file is invalid:")
        for i in bad_config_reasons:
            print(i, end="")

        message.warning("Falling back to default values for invalid items.")
