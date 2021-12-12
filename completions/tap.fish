# Completions for the `tap` command

set -l all_subcmds install update upgrade remove autoremove search list
set -l pkg_subcmds install upgrade search  
set -l installed_pkg_subcmds remove

function __fish_tap_subcommand
    set subcommand $argv[1]
    set -e argv[1]
    complete -f -c tap -n "not __fish_seen_subcommand_from $all_subcmds" -a $subcommand $argv
end

function __fish_tap_option
    set subcommand $argv[1]
    set -e argv[1]
    complete -f -c tap -n "__fish_seen_subcommand_from $subcommand" $argv
end

complete -c tap -n "__fish_seen_subcommand_from $pkg_subcmds" -a '(__fish_print_packages | head -n 250)'
complete -c tap -n "__fish_seen_subcommand_from $installed_pkg_subcmds" -a '(__fish_print_packages --installed | string match -re -- "(?:\\b|_)"(commandline -ct | string escape --style=regex) | head -n 250)' -d 'Package'

# Support flags
complete -x -f -c tap -s h -l help -d 'Display help'

# List
__fish_tap_subcommand list -d 'List installed packages'
__fish_tap_option list -s a -l apt-only -d 'Only show packages available via APT'
__fish_tap_option list -s h -l help -d 'Display help'
__fish_tap_option list -s i -l installed -d 'Only show installed packages'
__fish_tap_option list -s L -l skip-less-pipe -d 'Don\'t pipe output into \'less\' if output is larger than terminal height'
__fish_tap_option list -s m -l mpr-only -d 'Only show packages available in the MPR'
__fish_tap_option list -s p -l pkgname-only -d 'Only print package names'
__fish_tap_option list -s q -l quiet -d 'Hide information messages'
__fish_tap_option list -s a -l apt-only -d 'Only show packages available via APT'
__fish_tap_option list -s R -l rev-alpha -d 'Sort package results from Z-A instead of A-Z'
__fish_tap_option list -s u -l upgradable -d 'Only show upgradable packages'

# Search
__fish_tap_subcommand search -r -d 'Search for packages'
__fish_tap_option search -s a -l apt-only -d 'Only show packages available via APT'
__fish_tap_option search -s h -l help -d 'Display help'
__fish_tap_option search -s m -l mpr-only -d 'Only show packages available in the MPR'
__fish_tap_option search -s L -l skip-less-pipe -d 'Don\'t pipe output into \'less\' if output is larger than terminal height'
__fish_tap_option search -s p -l pkgname-only -d 'Only print package names'
__fish_tap_option search -s q -l quiet -d 'Hide information messages'
__fish_tap_option search -s R -l rev-alpha -d 'Sort package results from Z-A instead of A-Z'

# Install
__fish_tap_subcommand install -r -d 'Install packages'
__fish_tap_option install -s h -l help -d 'Display help'

# Remove
__fish_tap_subcommand remove -r -d 'Remove packages'
__fish_tap_option remove -s h -l help -d 'Display help'
__fish_tap_option remove -s p -l purge -d 'Remove configuration files for packages upon removal'

# Autoremove
__fish_tap_subcommand autoremove -d 'Remove packages no longer needed as dependencies'
__fish_tap_option autoremove -s h -l help -d 'Display help'

# Update
__fish_tap_subcommand update -x -d 'Update package list'
__fish_tap_option update -s h -l help -d 'Display help'

# Upgrade
__fish_tap_subcommand upgrade -r -d 'Upgrade packages'
__fish_tap_option upgrade -s a -l apt-only -d 'Only consider APT packages for upgrades'
__fish_tap_option upgrade -s h -l help -d 'Display help'
__fish_tap_option upgrade -s h -l mpr-only -d 'Only consider MPR packages for upgrades'
