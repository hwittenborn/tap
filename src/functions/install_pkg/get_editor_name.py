# Credits to @vyashole (GitHub) for the idea to implement this.
# See 'https://github.com/hwittenborn/tap/issues/2' for more info.

def get_editor_name():
	import os

	editor_name = ""

	# Per Debian policy, $VISUAL should be used instead of $EDITOR
	# when it is set. Likewise, we check for $VISUAL after $EDITOR,
	# which causes the recoreded editor to be the value of $VISUAL,
	# even if $EDITOR is set.
	for i in ['EDITOR', 'VISUAL']:
		environment_value = os.getenv(f"{i}")
		if environment_value != None:
			editor_name = environment_value

	if editor_name == "":
		editor_name = "/usr/bin/editor"

	if os.popen(f"command -v '{editor_name}'").read() == "":
		print(f"Couldn't find text editor '{editor_name}'.")
		quit(1)

	return editor_name
