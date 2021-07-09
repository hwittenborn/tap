def search_package(dur_url, packages):
	import requests
	import json
	import datetime

	request_arguments = ""

	for i in packages:
		request_arguments += i

	dur_rpc_request = requests.get("https://" + dur_url + "/rpc/?v=5&type=search&arg=" + request_arguments)

	try: dur_rpc_json_data = json.loads(dur_rpc_request.text)
	except json.decoder.JSONDecodeError:
		print("[JSON] There was an error processing your request.")
		quit(1)

	if dur_rpc_json_data["resultcount"] == 0:
		print("No results.")
		quit(0)

	number = 0

	while number < dur_rpc_json_data["resultcount"]:

		print(dur_rpc_json_data['results'][number]['Name'] + '/' + dur_rpc_json_data['results'][number]['Version'])
		print("  Description: " + dur_rpc_json_data['results'][number]['Description'])
		print("  Maintainer: " + dur_rpc_json_data['results'][number]['Maintainer'])
		print("  Votes: " + str(dur_rpc_json_data['results'][number]['NumVotes']))

		outofdate = dur_rpc_json_data['results'][number]['OutOfDate']
		if outofdate == None:
			print("  Out of Date: N/A")
		else:
			print("  Out of Date: " + datetime.datetime.fromtimestamp(outofdate).strftime('%Y-%m-%d'))

		lastmodified = dur_rpc_json_data['results'][number]['LastModified']
		print('  Last Modified: ' + datetime.datetime.fromtimestamp(lastmodified).strftime('%Y-%m-%d'))

		if (number + 1) < dur_rpc_json_data["resultcount"]:
			print()

		number = number + 1
