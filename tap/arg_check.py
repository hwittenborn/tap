import re
from sys import argv

from tap import cfg
from tap.help_menu import help_menu
from tap.message import message


def _split_args(args):
    returned_args = []

    for i in args:
        if re.match("^-[^-]", i) is not None:
            for j in i.lstrip("-"):
                returned_args += ["-" + j]
        else:
            returned_args += [i]

    return returned_args


def arg_check():
    options = []

    for i in _split_args(argv[1:]):
        if re.match("^[a-z0-9][a-z0-9-]*$", i) is not None:
            if cfg.operation is None:
                cfg.operation = i
            else:
                cfg.packages += [i]

        elif re.match("^-[a-zA-Z-]*$", i):
            options += [i]

        else:
            cfg.unknown_options += [i]

    # Remove any duplicate keys from the packages list.
    cfg.packages = list(set(cfg.packages))

    if cfg.operation is None:
        help_menu()

    elif cfg.operation not in cfg.available_commands:
        message.error(f"Invalid command '{cfg.operation}'.")
        message.error(f"See '{cfg.application_name} --help' for available commands.")
        exit(1)

    # Process sub-command arguments.
    opts = cfg.command_options[cfg.operation]
    available_options = opts[0]
    shortopt_mappings = opts[1]

    for i in options:
        if i in available_options:
            cfg.options += [i]
        elif i in shortopt_mappings:
            cfg.options += [shortopt_mappings[i]]
        else:
            cfg.unknown_options += [i]

    if cfg.unknown_options != []:
        for i in cfg.unknown_options:
            message.error(f"Unknown option '{i}'.")
        message.error(
            f"See '{cfg.application_name} {cfg.operation} --help' for available options."
        )
        exit(1)

    for i in ("-h", "--help"):
        if i in cfg.options:
            help_menu()

    # Check if a command recieved argument when it was/wasn't supposed to.
    if (cfg.operation in cfg.requires_arguments) and (cfg.packages == []):
        message.error(f"Command '{cfg.operation}' requires arguments.")
        exit(1)
    elif (
        (cfg.operation not in cfg.requires_arguments)
        and (cfg.operation not in cfg.optional_arguments)
        and (cfg.packages != [])
    ):
        message.error(f"Command '{cfg.operation}' doesn't take arguments.")
        exit(1)
