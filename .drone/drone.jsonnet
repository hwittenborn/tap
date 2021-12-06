local runUnitTests() = {
    name: "run-unit-tests",
    kind: "pipeline",
    type: "docker",

    steps: [{
        name: "run-unit-tests",
        image: "proget.hunterwittenborn.com/docker/makedeb/makedeb:ubuntu-focal",
        commands: [".drone/scripts/unit-tests.sh"]
    }]
};

local createTag() = {
    name: "create-release",
    kind: "pipeline",
    type: "docker",
    depends_on: ["run-unit-tests"],
    trigger: {branch: "main"},

    steps: [{
        name: "create-release",
        image: "python",
        environment: {
            github_api_key: {from_secret: "github_api_key"}
        },
        commands: [
            "pip install -r .drone/scripts/requirements.txt",
            ".drone/scripts/create-release.py"
        ]
    }]
};

local mprPublish() = {
	name: "mpr-publish",
	kind: "pipeline",
	type: "docker",
    depends_on: ["create-release"],
    trigger: {branch: "main"},

	steps: [{
		name: "publish-mpr",
		image: "proget.hunterwittenborn.com/docker/makedeb/makedeb:ubuntu-focal",
		environment: {
			ssh_key: {from_secret: "ssh_key"},
		},
		commands: [".drone/scripts/publish.sh"]
    }]
};


local sendNotification() = {
    name: "send-notification",
    kind: "pipeline",
    type: "docker",
    depends_on: ["mpr-publish"],
    trigger: {
        branch: "main",
        status: ["success", "failure"]
    },

    steps: [{
		name: "send-notification",
		image: "proget.hunterwittenborn.com/docker/hwittenborn/drone-matrix",
		settings: {
			username: "drone",
			password: {from_secret: "matrix_api_key"},
			homeserver: "https://matrix.hunterwittenborn.com",
			room: "#tap:hunterwittenborn.com"
		}
	}]
};

[
    runUnitTests(),
    createTag(),
	mprPublish(),
    sendNotification()
]
