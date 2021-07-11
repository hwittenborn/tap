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

		print(f"{colors.apt_green}{mpr_rpc_json_data['results'][number]['Name']}{colors.white}/{mpr_rpc_json_data['results'][number]['Version']}")
		print(f"  Description: {mpr_rpc_json_data['results'][number]['Description']}")
		print(f"  Maintainer: {mpr_rpc_json_data['results'][number]['Maintainer']}")
		print(f"  Votes: {str(mpr_rpc_json_data['results'][number]['NumVotes'])}")

		outofdate = mpr_rpc_json_data['results'][number]['OutOfDate']
		if outofdate == None:
			print("  Out of Date: N/A")
		else:
			print(f"  Out of Date: {datetime.datetime.fromtimestamp(outofdate).strftime('%Y-%m-%d')}")

		lastmodified = mpr_rpc_json_data['results'][number]['LastModified']
		print(f"  Last Modified: {datetime.datetime.fromtimestamp(lastmodified).strftime('%Y-%m-%d')}")

		if (number + 1) < mpr_rpc_json_data["resultcount"]:
			print()

		number = number + 1
