#!/usr/bin/env bash
set -ex
mpr_fingerprint='SHA256:TQtnFwjBwpDOHnHTaANeudpXVmomlYo6Td/8T51FA/w'

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

rm "tap-mpr/PKGBUILD"
cp "makedeb/PKGBUILD" "tap-mpr/PKGBUILD"
cd "tap-mpr"
makedeb --printsrcinfo | tee .SRCINFO

package_version="$(cat .SRCINFO | grep 'pkgver' | awk -F ' = ' '{print $2}')"
package_relationship="$(cat .SRCINFO | grep 'pkgrel' | awk -F ' = ' '{print $2}')"
git add PKGBUILD .SRCINFO
git commit -m "Updated version to ${package_version}-${package_relationship}"

git push
