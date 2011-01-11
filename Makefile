PLUGIN = orgmode

${PLUGIN}.vba.gz: test clean
	echo README > files
	echo LICENSE >> files
	find . -type f -name \*.py -o -type f -name \*.vim | sed -e 's/^\.\///' | grep -v '^test\/' | grep -v Example.py >> files
	vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vim
	gzip ${PLUGIN}.vba

test: test/orgmode-test.py
	cd test && python orgmode-test.py

clean:
	@rm -f ${PLUGIN}.vba.gz files

.PHONY: test clean
