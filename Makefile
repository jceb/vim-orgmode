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

check: tests/run_tests.py
	cd tests && python run_tests.py

coverage:
	cd tests && nosetests --with-coverage --cover-html .

clean: documentation
	@rm -rf ${PLUGIN}.vmb ${PLUGIN}.vmb.gz tmp files
	cd $^ && $(MAKE) $@

${PLUGIN}.vmb: check build_vmb.vim clean
	$(MAKE) DESTDIR=$(PWD)/tmp VIMDIR= install
	find tmp -type f  | sed -e 's/^tmp\///' > files
	cp build_vmb.vim tmp
	cd tmp && vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vmb.vim
	[ -e tmp/${PLUGIN}.vba ] && mv tmp/${PLUGIN}.vba tmp/$@ || true
	mv tmp/$@ .

${PLUGIN}.vmb.gz: ${PLUGIN}.vmb
	@rm -f ${PLUGIN}.vmb.gz
	gzip $^

vmb: ${PLUGIN}.vmb

vmb.gz: ${PLUGIN}.vmb.gz

docs: documentation
	cd $^ && $(MAKE)

installvmb: ${PLUGIN}.vmb install_vmb.vim
	rm -rvf ${VIMPLUGINDIR}
	mkdir -p "${VIMPLUGINDIR}"
	vim --cmd "let g:installdir='${VIMPLUGINDIR}'" -s install_vmb.vim $^
	@echo "Plugin was installed in ${VIMPLUGINDIR}. Make sure you are using a plugin loader like pathegon, otherwise the ${PLUGIN} might not work properly."

.PHONY: all build test check install clean vmb vmb.gz docs installvmb
