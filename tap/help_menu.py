from tap import cfg

def help_menu(**args):
    print(f"{cfg.application_name} {cfg.application_version} - MPR in your pocket")
    print()
    print(f"Usage: {cfg.application_name} [command] [packages/options]")
    print()
    print("Commands:")
    print("  install                 Install packages")
    print("  update                  Update local repository caches")
    print("  upgrade                 Upgrade currently installed packages")
    print("  remove                  Remove installed packages")
    print("  search                  Search for packages")
    print("  list-packages           List installed packages built from the MPR")
    print()
    print("Options:")
    print("  -e, --min-info          Print extra information when using 'search'")
    print("  -h, --help              Bring up this help menu")
    print("  -L, --skip-less-pipe    Don't pipe output from 'list-packages' into 'less' when output is taller than the terminal height")
    print("  -R, --rev-alpha         Sort results from 'search' and 'list-packages' from Z-A instead of A-Z")
    print("  -V, --version           Print version information and exit")
    print()
    print(f"See {cfg.application_name}(8) for more information on usage and links for support.")

    if args.get("exit", True):
        exit(0)
