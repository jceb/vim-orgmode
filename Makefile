PLUGIN = orgmode

PREFIX = /usr/local
VIMDIR = $(PREFIX)/share/vim

VIMPLUGINDIR = $(HOME)/.vim/bundle/orgmode

all: build

build:

install: doc indent ftdetect ftplugin syntax
	for i in doc indent ftdetect ftplugin syntax; do \
		find $$i -type f -name \*.txt -o -name \*.py -o -type f -name \*.vim | while read f; do \
			install -m 0755 -d $(DESTDIR)$(VIMDIR)/$$(dirname "$$f"); \
			install -m 0644 $$f $(DESTDIR)$(VIMDIR)/$$f; \
		done; \
	done

test: check

check: test/run_tests.py
	cd test && python run_tests.py

clean: documentation
	@rm -rf ${PLUGIN}.vba ${PLUGIN}.vba.gz tmp files
	cd $^ && $(MAKE) $@

${PLUGIN}.vba: check build_vba.vim clean
	$(MAKE) DESTDIR=$(PWD)/tmp VIMDIR= install
	find tmp -type f  | sed -e 's/^tmp\///' > files
	cp build_vba.vim tmp
	cd tmp && vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vba.vim
	[ -e tmp/${PLUGIN}.vmb ] && mv tmp/${PLUGIN}.vmb tmp/$@ || true
	mv tmp/$@ .

${PLUGIN}.vba.gz: ${PLUGIN}.vba
	@rm -f ${PLUGIN}.vba.gz
	gzip $^

vba: ${PLUGIN}.vba

vba.gz: ${PLUGIN}.vba.gz

docs: documentation
	cd $^ && $(MAKE)

installvba: ${PLUGIN}.vba install_vba.vim
	rm -rvf ${VIMPLUGINDIR}
	mkdir -p "${VIMPLUGINDIR}"
	vim --cmd "let g:installdir='${VIMPLUGINDIR}'" -s install_vba.vim $^
	@echo "Plugin was installed in ${VIMPLUGINDIR}. Make sure you are using a plugin loader like pathegon, otherwise the ${PLUGIN} might not work properly."

.PHONY: all build test check install clean vba vba.gz docs installvba
