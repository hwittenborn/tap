local mprPublish() = {
	name: "mpr-publish",
	kind: "pipeline",
	type: "docker",

	steps: [
		{
			name: "create-tag",
			image: "proget.hunterwittenborn.com/docker/hunter/makedeb:stable",
			environment: {
				ssh_key: {from_secret: "ssh_key"},
				known_hosts: {from_secret: "known_hosts"}
			},

			commands: [".drone/scripts/create_tag.sh"]
		},

		{
			name: "publish-mpr",
			image: "proget.hunterwittenborn.com/docker/hunter/makedeb:stable",
			environment: {
				ssh_key: {from_secret: "ssh_key"},
				known_hosts: {from_secret: "known_hosts"}
			},

			commands: [".drone/scripts/publish.sh"]
		}

	]
};

[
	mprPublish(),
]
