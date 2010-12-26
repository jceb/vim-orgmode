PLUGIN = orgmode

${PLUGIN}.vba:
	echo README > files
	echo LICENSE >> files
	find . -type f -name \*.py -o -type f -name \*.vim | sed -e 's/^\.\///' | grep -v '^test\/' >> files
	vim --cmd 'let g:plugin_name="${PLUGIN}"' -s build_vim

clean:
	@rm -f ${PLUGIN}.vba files
