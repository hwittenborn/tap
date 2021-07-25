def search_package(mpr_url, packages, application_name, application_version):
	import requests
	import json
	import datetime

	from functions.colors import colors    # REMOVE AT PACKAGING

	request_arguments = ""

	for i in packages:
		request_arguments += i

	mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=search&arg={request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})

	try: mpr_rpc_json_data = json.loads(mpr_rpc_request.text)
	except json.decoder.JSONDecodeError:
		print("[JSON] There was an error processing your request.")
		quit(1)

	if mpr_rpc_json_data["resultcount"] == 0:
		print("No results.")
		quit(0)

	number = 0

	while number < mpr_rpc_json_data["resultcount"]:

		# Get JSON data
		package_name = mpr_rpc_json_data['results'][number]['Name']
		package_version = mpr_rpc_json_data['results'][number]['Version']
		package_description = mpr_rpc_json_data['results'][number]['Description']
		package_maintainer = mpr_rpc_json_data['results'][number]['Maintainer']
		package_votes = mpr_rpc_json_data['results'][number]['NumVotes']

		outofdate = mpr_rpc_json_data['results'][number]['OutOfDate']
		if outofdate == None:
			package_outofdate = "N/A"
		else:
			package_outofdate = datetime.datetime.fromtimestamp(outofdate).strftime('%Y-%m-%d')

		package_lastmodified_json = mpr_rpc_json_data['results'][number]['LastModified']
		package_lastmodified = datetime.datetime.fromtimestamp(package_lastmodified_json).strftime('%Y-%m-%d')

		# Print generated text
		print(f"{colors.apt_green}{package_name}{colors.white}/{package_version}")
		print(f"  Description: {package_description}")
		print(f"  Maintainer: {package_maintainer}")
		print(f"  Votes: {package_votes}")
		print(f"  Out of Date: {package_outofdate}")
		print(f"  Last Modified: {package_lastmodified}")

		if (number + 1) < mpr_rpc_json_data["resultcount"]:
			print()

		number = number + 1
