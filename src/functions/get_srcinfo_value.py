def get_srcinfo_value(field, tabbing):
	import re

	field_value = []

	srcinfo_data = open('.SRCINFO', 'r').readlines()
	open('.SRCINFO', 'r').close()

	for i in srcinfo_data:
		if tabbing == True:
			string_results = re.findall(f"^\t{field} = .*", i)
		else:
			string_results = re.findall(f"^{field} = .*", i)

		if len(string_results) > 0:
			field_value += [string_results[0].split(' = ')[1]]

	return field_value
