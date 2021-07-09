# Maintainer: Hunter Wittenborn <hunter@hunterwittenborn.com>
pkgname=tap
pkgver=0.1.1
pkgrel=1
pkgdesc="MPR in your pocket"
arch=('any')
depends=('python3')
license=('GPL3')
url="https://github.com/hwittenborn/tap"

source=("${url}/archive/refs/tags/v0.1.tar.gz")
sha256sums=('SKIP')

package() {
	cd "${pkgname}-${pkgver}"

	# Create executable for tap
	mkdir -p "${pkgdir}/usr/bin/"
	echo '#!/usr/bin/env python3' > "${pkgdir}/usr/bin/tap"

	# Copy data from source files into executable
	for i in $(find "src/functions/" -type f | grep '\.py$'); do
		cat "${i}" >> "${pkgdir}/usr/bin/tap"
	done

	cat "src/main.py" >> "${pkgdir}/usr/bin/tap"

	# Remove testing commands
	sed -i 's|.*# REMOVE AT PACKAGING||' "${pkgdir}/usr/bin/tap"

	# Set perms on executable
	chmod 555 "${pkgdir}/usr/bin/tap"
}
