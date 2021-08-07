def generate_control_string(field, values):
	from functions.format_dependencies  import  format_dependencies    # REMOVE AT PACKAGING

	if len(values) == 0:
		return None

	control_packages = format_dependencies(values)

	control_string = f"{field}: {control_packages[0]}"

	for i in control_packages[1:]:
		control_string += f", {i}"

	return control_string