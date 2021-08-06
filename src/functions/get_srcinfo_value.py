def get_srcinfo_value(field):
	import re

	field_value = []

	srcinfo_data = open('.SRCINFO', 'r').readlines()
	open('.SRCINFO', 'r').close()

	for i in srcinfo_data:
		string_results = re.findall(f"^\t{field} = .*", i)

		if len(string_results) > 0:
			field_value += [string_results[0].split(' = ')[1]]

	return field_value
