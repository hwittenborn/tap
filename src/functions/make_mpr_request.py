def make_mpr_request(packages, mpr_url, application_name, application_version):
	import requests
	import json

	rpc_request_arguments = ""

	for i in packages:
		rpc_request_arguments += "&arg[]=" + i

	mpr_rpc_request = requests.get(f"https://{mpr_url}/rpc/?v=5&type=info{rpc_request_arguments}", headers={"User-Agent": f"{application_name}/{application_version}"})

	try:
		mpr_rpc_json_data = json.loads(mpr_rpc_request.text)

		if mpr_rpc_json_data['type'] == "error":
			print("[JSON] There was an error processing your request.")
			quit(1)

		return mpr_rpc_json_data

	except json.decoder.JSONDecodeError:
		print("[JSON] There was an error processing your request.")
		quit(1)
