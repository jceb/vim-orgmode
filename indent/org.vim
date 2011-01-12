" Delete the next line to avoid the special indention of items
if !exists("g:org_indent")
  let g:org_indent = 0
endif

setlocal foldtext=GetOrgFoldtext()
setlocal fillchars-=fold:-
setlocal fillchars+=fold:\ 
setlocal foldexpr=GetOrgFolding()
setlocal foldmethod=expr
setlocal indentexpr=GetOrgIndent()
setlocal nolisp
setlocal nosmartindent
setlocal autoindent

function! GetOrgIndent()
python << EOF
from orgmode import indent_orgmode
indent_orgmode()
EOF
	if exists('b:indent_level')
		let tmp = b:indent_level
		unlet b:indent_level
		return tmp
	else
		return -1
	endif
endfunction

function! GetOrgFolding()
python << EOF
from orgmode import fold_orgmode
fold_orgmode()
EOF
	if exists('b:fold_expr')
		let tmp = b:fold_expr
		unlet b:fold_expr
		return tmp
	else
		return -1
	endif
endfunction

function! GetOrgFoldtext()
python << EOF
from orgmode import fold_text
fold_text()
EOF
	if exists('b:foldtext')
		let tmp = b:foldtext
		unlet b:foldtext
		return tmp
	endif
endfunction
