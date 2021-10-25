# Credits to @vyashole (GitHub) for the idea to implement this.
# See 'https://github.com/hwittenborn/tap/issues/2' for more info.
def get_editor_name():
    from os import environ as env
    from shutil import which
    from tap.message import message

    # Per Debian policy, $VISUAL should be used instead of $EDITOR
    # when it is set. Likewise, we check for $VISUAL after $EDITOR,
    # which causes the recoreded editor to be the value of $VISUAL,
    # even if $EDITOR is set.
    editor_name = None

    for i in ['EDITOR', 'VISUAL']:
        value = env.get(i)
        
        if value is not None:
            editor_name = value
    
    if editor_name is None:
        editor_name = "/usr/bin/editor"

    if which(editor_name) is None:
        message("error", f"Couldn't find editor '{editor_name}'.")
        quit(1)

    return editor_name
