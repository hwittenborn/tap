def make_mpr_request(packages, mpr_url, application_name, application_version):
	import requests
	import json

	from tap.message import message # REMOVE AT PACKAGING

	rpc_request_arguments = ""

	for i in packages:
		rpc_request_arguments += "&arg[]=" + i

	try:
		mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=info{rpc_request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})
	except requests.exceptions.ConnectionError:
		message("error", "Failed to make request to MPR.")
		quit(1)

	try:
		mpr_rpc_json_data = json.loads(mpr_rpc_request.text)

		if mpr_rpc_json_data['type'] == "error":
			message("error", "[JSON] There was an error processing your request.")
			quit(1)

		return mpr_rpc_json_data

	except json.decoder.JSONDecodeError:
		message("error", "[JSON] There was an error processing your request.")
		quit(1)
