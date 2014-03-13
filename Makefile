PLUGIN = orgmode
PREFIX = /usr/local
VIMDIR = $(PREFIX)/share/vim

all: build

build:

# install plugin at destination
install: doc indent ftdetect ftplugin syntax
	for i in doc indent ftdetect ftplugin syntax; do \
		find $$i -type f -name \*.txt -o -type f -name \*.cnf -o -type f -name \*.py -o -type f -name \*.vim | while read f; do \
			install -m 0755 -d $(DESTDIR)$(VIMDIR)/$$(dirname "$$f"); \
			install -m 0644 $$f $(DESTDIR)$(VIMDIR)/$$f; \
		done; \
	done

# cleanup
clean: documentation
	@find . -name \*.pyc -o -name \*.py,cover -exec rm {} \;
	@rm -rf ${PLUGIN}.vmb ${PLUGIN}.vmb.gz tmp files
	cd $< && $(MAKE) $@

# generate the vim ball package
${PLUGIN}.vmb: check build_vmb.vim clean
	$(MAKE) DESTDIR=$(PWD)/tmp VIMDIR= install
	find tmp -type f  | sed -e 's/^tmp\///' > files
	cp build_vmb.vim tmp
	cd tmp && vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vmb.vim
	[ -e tmp/${PLUGIN}.vba ] && mv tmp/${PLUGIN}.vba tmp/$@ || true
	mv tmp/$@ .

${PLUGIN}.vmb.gz: ${PLUGIN}.vmb
	@rm -f ${PLUGIN}.vmb.gz
	gzip $<

vmb: ${PLUGIN}.vmb

vmb.gz: ${PLUGIN}.vmb.gz

${PLUGIN}.vba: ${PLUGIN}.vmb
	mv $< $@

${PLUGIN}.vba.gz: ${PLUGIN}.vba
	@rm -f ${PLUGIN}.vba.gz
	gzip $<

vba: ${PLUGIN}.vba

vba.gz: ${PLUGIN}.vba.gz

# run unit tests
test: check

check: tests/run_tests.py
	cd tests && python2 run_tests.py

# generate documentation
docs: documentation
	cd $< && $(MAKE)

# generate a test coverage report for all python files
coverage:
	@echo ">>> Coverage depends on the package python-nose and python-coverage, make sure they are installed!"
	cd tests && nosetests2 --with-coverage --cover-html .

# run a static code checker
lint:
	@echo ">>> Lint depends on the package pylint make sure it's installed!"
	pylint --rcfile .pylintrc --disable=C0301,C0103,C0111,C0322,C0323,C0324,W0703,W0612,W0603 orgmode

lintall:
	@echo ">>> Lint depends on the package pylint make sure it's installed!"
	pylint --rcfile .pylintrc orgmode

# install vim-orgmode in the .vim/bundle directory for test purposes
VIMPLUGINDIR = $(HOME)/.vim/bundle/orgmode

installvmb: ${PLUGIN}.vmb install_vmb.vim
	rm -rvf ${VIMPLUGINDIR}
	mkdir -p "${VIMPLUGINDIR}"
	vim --cmd "let g:installdir='${VIMPLUGINDIR}'" -s install_vmb.vim $<
	@echo "Plugin was installed in ${VIMPLUGINDIR}. Make sure you are using a plugin loader like pathegon, otherwise the ${PLUGIN} might not work properly."

installvba: ${PLUGIN}.vba install_vba.vim
	rm -rvf ${VIMPLUGINDIR}
	mkdir -p "${VIMPLUGINDIR}"
	vim --cmd "let g:installdir='${VIMPLUGINDIR}'" -s install_vba.vim $<
	@echo "Plugin was installed in ${VIMPLUGINDIR}. Make sure you are using a plugin loader like pathegon, otherwise the ${PLUGIN} might not work properly."

.PHONY: all build test check install clean vmb vmb.gz docs installvmb
