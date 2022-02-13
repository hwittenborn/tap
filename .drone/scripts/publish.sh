#!/usr/bin/env bash
set -ex
mpr_fingerprint='SHA256:7Wki/ZTENAVOYmAtH4+vhqZB8vHkLURS+eK1SQy0jTs'

# SSH configuration
rm -rf "${HOME}/.ssh/" || true
mkdir -p "${HOME}/.ssh/"

echo "${ssh_key}" > "${HOME}/.ssh/ssh_key"
chmod 400 "${HOME}/.ssh/ssh_key"
printf "Host ${mpr_url}\n  Hostname ${mpr_url}\n  IdentityFile ${HOME}/.ssh/ssh_key\n" | tee "${HOME}/.ssh/config"

SSH_HOST="${mpr_url}" \
SSH_EXPECTED_FINGERPRINT="${mpr_fingerprint}" \
SET_PERMS="true" \
get-ssh-key

# Git stuff.
git config --global user.name "Kavplex Bot"
git config --global user.email "kavplex@hunterwittenborn.com"

git clone "ssh://mpr@${mpr_url}/tap.git" "tap-mpr"

cd tap-mpr/
find ./ \
     -maxdepth 1 \
     -not -path './' \
     -not -path './.git' \
     -exec rm '{}' -rfv \;

cd ../makedeb/
find ./ \
    -maxdepth 1 \
    -exec cp '{}' '../tap-mpr/{}' -Rv \;

cd ../tap-mpr/
makedeb --printsrcinfo | tee .SRCINFO

package_version="$(cat .SRCINFO | grep 'pkgver' | awk -F ' = ' '{print $2}')"
package_relationship="$(cat .SRCINFO | grep 'pkgrel' | awk -F ' = ' '{print $2}')"
git add ./
git commit -m "Updated version to ${package_version}-${package_relationship}"

git push
