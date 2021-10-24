def get_control_field_value(package, field):
	import re

	field_value = []

	file = open(f"/var/tmp/mpm/build_dir/{package}/pkg/{package}/DEBIAN/control", "r")
	control_data = file.readlines()
	file.close()

	for i in control_data:
		string = re.match(f"^{field}:.*", i)

		if string == None:
			continue

		else:
			string_value = re.sub(f"^{field}: ", "", string.group(0))
			break

	return string_value.split(', ')
