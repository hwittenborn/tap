import configparser
from os.path import exists

from tap import cfg
from tap.message import message


def get_config_item(section, key, **kwargs):
    config_item = cfg.config_data.get(section)

    if config_item is not None:
        config_item = config_item.get(key)

    try:
        if int(config_item) == 1:
            return True
        return False
    except (ValueError, TypeError):
        return False


def get_option(section, key):
    cli_arg = "--" + key.replace("_", "-")

    if cli_arg in cfg.options:
        return True

    if get_config_item(section, key):
        return True

    return False


def read_config():
    config = configparser.ConfigParser()

    if not exists(cfg.config_file):
        if "--quiet" not in cfg.options:
            message.warning(
                "Couldn't find config file, falling back to default values."
            )
        cfg.config_data = {}
        return

    config.read(cfg.config_file)
    config_dict = {}

    for item in config.sections():
        current_dict = {}

        for key in config[item]:
            current_dict[key] = config[item][key]

        config_dict[item] = current_dict

    cfg.config_data = config_dict
