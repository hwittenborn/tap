MAN_SOURCE_DATE_EPOCH = $(shell git log -1 --pretty='%ct' ./man/tap.8.adoc)

prepare:
	sed -i 's|{pkgver}|$(PKGVER)|' ./tap.py
	sed -i 's|{pkgver}|$(PKGVER)|' ./man/tap.8.adoc

install:
	install -Dm 755 ./tap.py '$(DESTDIR)/usr/bin/tap'
	./setup.py install --prefix='./usr' --root='$(DESTDIR)' --install-layout='deb'
	
	SOURCE_DATE_EPOCH='$(MAN_SOURCE_DATE_EPOCH)' asciidoctor -b manpage ./man/tap.8.adoc -o '$(DESTDIR)/usr/share/man8/tap.8'
	install -Dm 555 'completions/tap.bash' '$(DESTDIR)/usr/share/bash-completion/completions/tap'
	install -Dm 644 'tap.cfg' '$(DESTDIR)/etc/tap.cfg'
	
	mkdir -p '$(DESTDIR)/var/cache/tap/'
	touch '$(DESTDIR)/var/cache/tap/mpr-cache.json'
	chmod 644 '$(DESTDIR)/var/cache/tap/mpr-cache.json'
	touch '$(DESTDIR)/var/cache/tap/pkglist'
	chmod 644 '$(DESTDIR)/var/cache/tap/pkglist'
