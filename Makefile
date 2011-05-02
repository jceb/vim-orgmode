PLUGIN = orgmode

PREFIX = /usr/local
VIMDIR = $(PREFIX)/share/vim

all: build

build:

install:
	for i in indent ftdetect ftplugin syntax; do \
		find $$i -type f -name \*.py -o -type f -name \*.vim | while read f; do \
			install -m 0755 -d $(DESTDIR)$(VIMDIR); \
			install -m 0644 $$f $(DESTDIR)$(VIMDIR)/$$f; \
		done; \
	done

check: test/run_tests.py
	cd test && python run_tests.py

clean: documentation
	@rm -rf ${PLUGIN}.vba.gz tmp
	cd $^ && $(MAKE) $@

${PLUGIN}.vba.gz: check
	$(MAKE) DESTDIR=$(PWD)/tmp VIMDIR= install
	echo $(PWD)
	find tmp -type f | sed -e 's/^tmp\/// '> tmp/files
	cp build_vim tmp
	cd tmp && vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vim && gzip ${PLUGIN}.vba
	mv tmp/$@ .

vba: ${PLUGIN}.vba.gz

docs: documentation
	cd $^ && $(MAKE)

.PHONY: all build check install clean vba docs
