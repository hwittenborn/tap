MAN_SOURCE_DATE_EPOCH != git log -1 --pretty='%ct' ./man/tap.8.adoc

prepare:
	sed -i "s|{pkgver}|$(PKGVER)|" ./tap.py
	sed -i "s|{pkgver}|$(PKGVER)|" ./man/tap.8.adoc

install:
	install -Dm 755 ./tap.py "$(DESTDIR)/usr/bin/tap"
	./setup.py install --prefix="./usr" --root="$(DESTDIR)" --install-layout="deb"
	SOURCE_DATE_EPOCH="$(MAN_SOURCE_DATE_EPOCH)" asciidoctor -b manpage ./man/tap.8.adoc -o "$(DESTDIR)/usr/share/man8/tap.8"
	install -Dm 555 "completions/tap.bash" "$(DESTDIR)/usr/share/bash-completion/completions/tap"
