#!/usr/bin/env bash
_tap() {
	number_of_args="${COMP_CWORD}"

	# Get current full value
	current_value="$(eval echo "\${COMP_WORDS[$(( $number_of_args - 1 ))]}")"

	# This gets triggered if a user is in the middle of writing an argument
	next_value="$(eval echo "\${COMP_WORDS[$number_of_args]}")"

	# Return available commands if only 'tap' is specified
	if [[ "${number_of_args}" == "1" ]]; then

		COMPREPLY=('install' 'update' 'upgrade' 'search' 'list-packages')

		if [[ "${next_value}" != "" ]]; then
			COMPREPLY=($(echo "${COMPREPLY[@]}" | sed 's| |\n|g' | grep "^${next_value}"))
		fi

		return
	fi

	# Check that a valid command was passed
	specified_command="${COMP_WORDS[1]}"

	for i in 'install' 'update' 'upgrade' 'search' 'list-packages'; do
		if [[ "${specified_command}" == "${i}" ]]; then
			valid_command="true"
		fi
	done

	if [[ "${valid_command}" != "true" ]]; then
		COMPREPLY=()
		return
	fi

	# Auto-fill for packages when using 'install'.
	# Uses 'specified_command' from the command validation above.
	if [[ "${specified_command}" == "install" && "${next_value}" != "" ]]; then

		mpr_json_data="$(curl -s "https://mpr.hunterwittenborn.com/rpc/?v=5&type=search&arg=${next_value}")"

		# Return nothing if returned JSON is not valid
		if ! echo "${mpr_json_data}" | jq &> /dev/null; then
			COMPREPLY=()
			return
		fi

		# Return package list.
		mpr_json_package_names="$(echo "${mpr_json_data}" | jq -r '.results[].Name' | grep "^${next_value}")"

		COMPREPLY=(${mpr_json_package_names})
		return
	fi
}

complete -F _tap tap
