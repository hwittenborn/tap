import re
from sys import argv

from tap import cfg
from tap.help_menu import help_menu
from tap.message import message

shortopts = {
    "-e": "--min-info",
    "-h": "--help",
    "-L": "--skip-less-pipe",
    "-R": "--rev-alpha",
    "-V": "--version",
}


def _split_args(args):
    returned_args = []

    for i in args:
        if re.match("-[^-]", i) is not None:
            for j in i.lstrip("-"):
                returned_args += ["-" + j]
        else:
            returned_args += [i]

    return returned_args


def arg_check():
    for i in _split_args(argv[1:]):
        if re.match("^[a-z][a-z-]*$", i) is not None:
            if cfg.operation is None:
                cfg.operation = i
            else:
                cfg.packages += [i]

        elif re.match("^-[a-zA-Z]*$", i):
            if i in shortopts.keys():
                cfg.options += [shortopts[i]]
            else:
                cfg.unknown_options += [i]

        elif re.match("^--[a-zA-Z][a-zA-Z-]*$", i):
            if i in shortopts.values():
                cfg.options += [i]
            else:
                cfg.unknown_options += [i]

        else:
            cfg.unknown_options += [i]

    # Remove any duplicate keys from the packages list.
    cfg.packages = list(set(cfg.packages))

    # Process arguments.
    if cfg.unknown_options != []:
        for i in cfg.unknown_options:
            message.error(f"Unknown option '{i}'.")
        message.error(f"See '{cfg.application_name} --help' for available commands.")
        exit(1)

    elif (cfg.operation is None) or ("--help" in cfg.options):
        help_menu()

    elif cfg.operation not in cfg.available_commands:
        message.error(f"Unknown command '{cfg.operation}'.")
        message.error(f"See '{cfg.application_name} --help' for available commands.")
        exit(1)

    elif (cfg.operation in cfg.requires_arguments) and (cfg.packages == []):
        message.error(f"Command '{cfg.operation}' requires arguments.")
        exit(1)

    elif (cfg.operation not in cfg.requires_arguments) and (cfg.packages != []):
        message.error(f"Command '{cfg.operation}' takes no arguments.")
        exit(1)
