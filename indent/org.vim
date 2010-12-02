" Delete the next line to avoid the special indention of items
if !exists("g:org_indent")
  let g:org_indent = 0
endif

setlocal indentexpr=GetOrgIndent()
setlocal nolisp
setlocal nosmartindent
setlocal autoindent

function! GetOrgIndent()
python << EOF
import vim
from orgmode.heading import Heading, DIRECTION_BACKWARD

res = -1
try:
	line = int(vim.eval('v:lnum'))
	h = Heading.find_heading(line - 1, direction=DIRECTION_BACKWARD)
	if h and line != h.start + 1:
		res = h.level + 1
except Exception, e:
	pass

if res != -1:
	vim.command('let b:indent_level = %d' % res)
EOF
if exists('b:indent_level')
	let tmp = b:indent_level
	unlet b:indent_level
	return tmp
else:
	return -1
endif
endfunction
