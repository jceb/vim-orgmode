PLUGIN = orgmode

PREFIX = /usr/local
VIMDIR = $(PREFIX)/share/vim

all: build

build:

install:
	for i in indent ftdetect ftplugin syntax; do \
		find $$i -type f -name \*.py -o -type f -name \*.vim | while read f; do \
			install -m 0644 -D $$f $(DESTDIR)$(VIMDIR)/$$f; \
		done; \
	done

check: test/orgmode-test.py
	cd test && python orgmode-test.py

clean:
	@rm -rf ${PLUGIN}.vba.gz tmp

${PLUGIN}.vba.gz: check
	$(MAKE) DESTDIR=$(PWD)/tmp VIMDIR= install
	echo $(PWD)
	find tmp -type f | sed -e 's/^tmp\/// '> tmp/files
	cp build_vim tmp
	cd tmp && vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vim && gzip ${PLUGIN}.vba
	mv tmp/$@ .

vba: ${PLUGIN}.vba.gz

.PHONY: all build check install clean vba
