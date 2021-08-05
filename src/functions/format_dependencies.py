def format_dependencies(dependencies):
	import re

	package_list = []

	for i in dependencies:

		for j in ['<=', '>=', '<', '>', '=']:

			try:
				relationship_type = re.search(j, i).group(0)
				break

			except AttributeError:
				if j == '=':
					# Needs to be set to a relationship (even when non is found)
					# for the regex check on 'package_version' below.
					relationship_type = "="
				continue

		try:
			dependency_name = re.search(f"^.*{relationship_type}", i).group(0).replace(relationship_type, '')
			dependency_version = re.search(f"{relationship_type}.*$", i).group(0).replace(relationship_type, '')

			package_list += [f"{dependency_name} ({relationship_type} {dependency_version})"]

		except AttributeError:
			package_list += [f"{i}"]

	return package_list