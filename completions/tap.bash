#!/usr/bin/env bash
_tap() {
    base_commands=('install' 'update' 'upgrade' 'remove'
                   'autoremove' 'search')

    accepts_args=('install' 'remove' 'search')
    install_opts=('-h' '--help')
    update_opts=('-h' '--help')
    upgrade_opts=('-h' '--help')
    remove_opts=('-h' '--help' '--purge')
    autoremove_opts=('-h' '--help')
    search_opts=('-h' '--help' '-R' '--rev-alpha'
                 '-L' '--skip-less-pipe' '--apt-only' '--mpr-only'
                 '-q' '--quiet' '--pkgname-only')
    list_opts=('-h' '--help' '-R' '--rev-alpha'
               '-L' '--skip-less-pipe' '--apt-only' '--mpr-only'
               '-q' '--quiet' '--pkgname-only' '--installed'
               '--upgradable')

    number_of_args="${#COMP_WORDS[@]}"
    command="${COMP_WORDS[1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    
    # Process very first arg.
    if [[ "${number_of_args}" == "2" ]]; then
        mapfile -t COMPREPLY < <(printf '%s\n' "${base_commands[@]}" | grep "^${cur}" 2> /dev/null)
        return
    fi

    # Process command options (if it's a valid command).
    valid_command=0

    for i in "${base_commands[@]}"; do
        if [[ "${command}" == "${i}" ]]; then
            valid_command=1
            break
        fi
    done

    if ! (( "${valid_command}" )); then
        COMPREPLY=()
        return
    fi
    
    opts="${command}_opts[@]"

    mapfile -t COMPREPLY < <(printf '%s\n' "${!opts}" | grep "^${cur}" 2> /dev/null)
    return
}

complete -F _tap tap
