from tap import cfg

def _print_formatted_args(args):
    total_length = 0

    for i in args:
        string_length = len(i)

        if string_length > total_length:
            total_length = string_length

    for i in args:
        extra_spaces = " " * (total_length - len(i))
        item_description = args[i]

        print(f"  {i}{extra_spaces}  {item_description}")

def help_menu(**args):
    print(f"Tap ({cfg.application_version}) - MPR in your pocket")
    print()
    
    if cfg.operation is None:
        print(f"Usage: {cfg.application_name} [command] [packages/options]")
        print()
        print("Commands:")
        _print_formatted_args(cfg.available_commands)

    else:
        opts = cfg.command_options[cfg.operation]
        long_opts = opts[0]
        short_opts = opts[1]

        combined_opts_dict = {}

        for opt in long_opts:
            extra_short_opts = []
            opt_desc = long_opts[opt]

            for short_opt in short_opts:
                if short_opts[short_opt] == opt:
                    extra_short_opts += [short_opt]

            new_opt = ", ".join(extra_short_opts + [opt])

            combined_opts_dict[new_opt] = opt_desc
        
        if cfg.operation in cfg.requires_arguments:
            print(f"Usage: {cfg.application_name} {cfg.operation} [packages/options]")
        else:
            print(f"Usage: {cfg.application_name} {cfg.operation} [options]")
        
        print()
        print("Options:")
        _print_formatted_args(combined_opts_dict)
    
    print()
    print(f"See {cfg.application_name}(8) for more information on usage and links for support.")

    if args.get("exit", True):
        exit(0)
