#!/usr/bin/env bash
_gen_compreply() {
    mapfile -t COMPREPLY < <(compgen -W "${1}" -- "${2}")
}

_pkglist_compreply() {
    tmpfile="$(mktemp)"
    mapfile -t pkglist < /var/cache/tap/pkglist
    compgen -W '${pkglist[@]}' -- "${cur}" > "${tmpfile}"
    mapfile -t COMPREPLY < "${tmpfile}"
}

_tap() {
    commands=('install' 'update' 'upgrade' 'remove' 'search' 'list')
    help_opts=('--help')
    upgrade_opts=('--apt-only' '--mpr-only')
    remove_opts=('--purge' '--autoremove')
    search_opts=('--rev-alpha' '--skip-less-pipe' '--apt-only' '--mpr-only' '--quiet' '--pkgname-only')
    list_opts=("${search_opts[@]}" '--installed' '--upgradable')

    local cur prev words cword
    _init_completion || return
    cmd="${words[1]}"

    case "${cmd}" in
        install|remove|list)
            case "${cur}" in
                -*)
                    cmd_opts="${cmd}_opts[@]"
                    opts=("${!cmd_opts}" "${help_opts[@]}")
                    _gen_compreply '${opts[@]}' "${cur}"
                    return
                    ;;

                *)
                    _pkglist_compreply
                    return
                    ;;
            esac
            ;;

        update|upgrade|search)
            cmd_opts="${cmd}_opts[@]"
            opts=("${!cmd_opts}" "${help_opts[@]}")
            _gen_compreply '${opts[@]}' "${cur}"
            return
            ;;

        *)
            _gen_compreply '${commands[@]}' "${cmd}"
            return
            ;;
    esac
}

complete -F _tap tap
