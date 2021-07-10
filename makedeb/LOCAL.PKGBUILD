# Maintainer: Hunter Wittenborn

# This PKGBUILD is used for local testing of tap. Variables are sourced
# from the DUR PKGBUILD, and then addition development variables and
# functions are applied.
source DUR.PKGBUILD

# Get local path info
_gitdir="$(git rev-parse --show-toplevel)"
_foldername="$(basename "${_gitdir}")"

source=("git+file://${_gitdir}")
sha256sums=('SKIP')

package() {
	# Create executable for tap
	mkdir -p "${pkgdir}/usr/bin/"
	echo '#!/usr/bin/env python3' > "${pkgdir}/usr/bin/tap"

	# Copy tap commands/functions into tap file
	cd "${_foldername}"

	for i in $(find src/functions/ -type f | grep '\.py$'); do
		cat "${i}" >> "${pkgdir}/usr/bin/tap"
	done

	cat "src/main.py" >> "${pkgdir}/usr/bin/tap"

	# Remove testing commands
	sed -i 's|.*# REMOVE AT PACKAGING||' "${pkgdir}/usr/bin/tap"

	# Set package version
	sed -i "s|application_version =.*|application_version = '${pkgver}-${pkgrel}'|" "${pkgdir}/usr/bin/tap"

	# Set perms on executable
	chmod 555 "${pkgdir}/usr/bin/tap"
}
