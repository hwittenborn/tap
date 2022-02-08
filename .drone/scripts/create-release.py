#!/usr/bin/env python3

import sys
from os import environ
from github import Github
from github.GithubException import BadCredentialsException
from github.Repository import Repository

# Get all the info we need.
github_api_key = environ.get("github_api_key")
drone_repo = "hwittenborn/tap"

with open(".SRCINFO") as file:
    pkgver = None
    pkgrel = None

    for i in file.read().splitlines():
        if i.startswith("\tpkgver"):
            pkgver = i
        elif i.startswith("\tpkgrel"):
            pkgrel = i

missing_var = False

for i in [[pkgver, "pkgver"], [pkgrel, "pkgrel"]]:
    var = i[0]
    var_name = i[1]

    if i is None:
        print(f"ERROR: '{i}' wasn't found in the .SRCINFO file.")
        missing_var = True

if missing_var:
    sys.exit(1)

pkgver = pkgver.lstrip("\tpkgver = ")
pkgrel = pkgrel.lstrip("\tpkgrel = ")

if github_api_key is None:
    print("ERROR: Environment variable 'github_api_key' isn't set.")
    sys.exit(1)

client = Github(github_api_key)

try:
    client.get_user().name
except BadCredentialsException:
    print("ERROR: Invalid credentials provided.")
    sys.exit(1)

# Create the release.
tag = f"v{pkgver}-{pkgrel}"
name = tag
message = f"Released {tag}."

repo = client.get_repo(drone_repo)
release = Repository.create_git_release(repo, tag, name, message)
