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
		let l:tmp = b:indent_level
		unlet b:indent_level
		return l:tmp
	else
		return -1
	endif
endfunction

function! GetOrgFolding()
	if mode() == 'i'
		" the cache size is limited to 3, because vim queries the current and
		" both surrounding lines when the user is typing in insert mode. The
		" cache is shared between GetOrgFolding and GetOrgFoldtext
		if ! exists('b:org_folding_cache')
			let b:org_folding_cache = {}
		endif

		if has_key(b:org_folding_cache, v:lnum)
			return b:org_folding_cache[v:lnum][0]
		endif
python << EOF
from orgmode import fold_orgmode
fold_orgmode(allow_dirty=True)
EOF
	else
		"unlet! b:org_folding_cache
python << EOF
from orgmode import fold_orgmode
fold_orgmode()
EOF
	endif

	if exists('b:fold_expr')
		let l:tmp = b:fold_expr
		unlet b:fold_expr
		if exists('b:org_folding_cache')
			if len(b:org_folding_cache) > 3
				let b:org_folding_cache = {}
			endif
			if ! has_key(b:org_folding_cache, v:lnum)
				let b:org_folding_cache[v:lnum] = [l:tmp]
			endif
		endif
		return l:tmp
	else
		return -1
	endif
endfunction

function! SetOrgFoldtext(text)
	let b:foldtext = a:text
endfunction

function! GetOrgFoldtext()
	if mode() == 'i'
		" the cache size is limited to 3, because vim queries the current and
		" both surrounding lines when the user is typing in insert mode. The
		" cache is shared between GetOrgFolding and GetOrgFoldtext
		if ! exists('b:org_folding_cache')
			let b:org_folding_cache = {}
		endif

		if has_key(b:org_folding_cache, v:lnum) &&
					\ len(b:org_folding_cache[v:lnum]) == 2
			return b:org_folding_cache[v:lnum][1]
		endif
python << EOF
from orgmode import fold_text
fold_text(allow_dirty=True)
EOF
	else
		"unlet! b:org_folding_cache
python << EOF
from orgmode import fold_text
fold_text()
EOF
	endif

	if exists('b:foldtext')
		let l:tmp = b:foldtext
		unlet b:foldtext
		if exists('b:org_folding_cache')
			if len(b:org_folding_cache) > 3
				let b:org_folding_cache = {}
			endif
			if has_key(b:org_folding_cache, v:lnum) &&
					\ len(b:org_folding_cache[v:lnum]) == 1
				let add(b:org_folding_cache[v:lnum], l:tmp)
			endif
		endif
		return l:tmp
	endif
endfunction
