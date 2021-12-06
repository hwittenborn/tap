local runUnitTests() = {
    name: "run-unit-tests",
    kind: "pipeline",
    type: "docker",

    steps: [{
        name: "run-unit-tests",
        image: "proget.hunterwittenborn.com/docker/makedeb/makedeb:ubuntu-focal",
        commands: [
        "sudo chown 'makedeb:makedeb' ./ -R",
        ".drone/scripts/unit-tests.sh"
        ]
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
        image: "proget.hunterwittenborn.com/docker/makedeb/makedeb:ubuntu-focal",
        environment: {
            github_api_key: {from_secret: "github_api_key"}
        },
        commands: [
            "sudo apt-get install python3-pip -y",
            "sudo chown 'makedeb:makedeb' ./ -R",
            "cd makedeb/",
            "makedeb --print-srcinfo > ../.SRCINFO",
            "cd ../",
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
		commands: [
            "curl -Ls \"https://shlink.$${hw_url}/ci-utils\" | sudo bash -",
            "sudo chown 'makedeb:makedeb' ./ -R",
            ".drone/scripts/publish.sh"
        ]
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
