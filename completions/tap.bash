#!/usr/bin/env bash
_tap() {
    base_commands=('install' 'update' 'upgrade' 'remove'
                   'autoremove' 'search' 'list')
    uses_pkglist=('install' 'remove' 'search' 'list')
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

    tmpfile="$(mktemp)"

    local cur prev words cword
    _init_completion || return
    cmd="${words[1]}"
    
    if [[ "${#words[@]}" == "2" ]]; then
        mapfile -t COMPREPLY < <(compgen -W '${base_commands[@]}' -- "${cur}")
        return
    fi

    if [[ "$(compgen -W '${base_commands[@]}' -- "${cmd}")" == "" ]]; then
        COMPREPLY=()
        return
    fi

    opts="${cmd}_opts[@]"

    case "${cur}" in
        -*)
            mapfile -t COMPREPLY < <(compgen -W '${!opts}' -- "${cur}")
            return
            ;;
        *)
            if [[ "$(compgen -W '${uses_pkglist[@]}' -- "${cmd}")" == "" ]]; then
                mapfile -t COMPREPLY < <(compgen -W '${!opts}' -- "${cur}")
                return
            fi

            mapfile -t pkglist < /var/cache/tap/pkglist
            compgen -W '${pkglist[@]}' -- "${cur}" > "${tmpfile}"
            mapfile -t COMPREPLY < "${tmpfile}"
            return
            ;;
    esac
}

complete -F _tap tap
