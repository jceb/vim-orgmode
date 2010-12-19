function! s:SynStars(perlevel)
	let b:levelstars = a:perlevel
	exe 'syntax match OL1 +^\(*\)\{1}\s.*+ contains=stars'
	exe 'syntax match OL2 +^\(*\)\{'.( 1 + 1*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL3 +^\(*\)\{'.(1 + 2*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL4 +^\(*\)\{'.(1 + 3*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL5 +^\(*\)\{'.(1 + 4*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL6 +^\(*\)\{'.(1 + 5*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL7 +^\(*\)\{'.(1 + 6*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL8 +^\(*\)\{'.(1 + 7*a:perlevel).'}\s.*+ contains=stars'
	exe 'syntax match OL9 +^\(*\)\{'.(1 + 8*a:perlevel).'}\s.*+ contains=stars'
endfunction
command! ChangeSyn  call <SID>SynStars(b:levelstars)

syntax match Properties +^\s*:\s*\S\{-1,}\s*:+
hi Properties guifg=pink
syntax match Tags +\s*:\S*:\s*$+
hi Tags guifg=pink
syntax match Dates +<\d\d\d\d-\d\d-\d\d.\{-1,}>+
hi Dates guifg=magenta
syntax match stars +\*\+\*+me=e-1 contained
if &background == 'light'
	hi stars guifg=#888888
else
	hi stars guifg=#444444
endif
syntax match NEXT '\* \zsNEXT' containedin=OL1,OL2,OL3,OL4,OL5,OL6,OL7,OL8,OL9
syntax match CANCELED '\* \zsCANCELED' containedin=OL1,OL2,OL3,OL4,OL5,OL6,OL7,OL8,OL9
syntax match TODO '\* \zsTODO' containedin=OL1,OL2,OL3,OL4,OL5,OL6,OL7,OL8,OL9
syntax match STARTED '\* \zsSTARTED' containedin=OL1,OL2,OL3,OL4,OL5,OL6,OL7,OL8,OL9
syntax match DONE '\* \zsDONE' containedin=OL1,OL2,OL3,OL4,OL5,OL6,OL7,OL8,OL9
"syntax match source '^#+\(begin\|end\)_src.*$' contained
"hi source gui=underline
syntax match OL1 +^\(*\)\{1}\s.*+ contains=stars
syntax match OL2 +^\(*\)\{2}\s.*+ contains=stars
syntax match OL3 +^\(*\)\{3}\s.*+ contains=stars
syntax match OL4 +^\(*\)\{4}\s.*+ contains=stars
syntax match OL5 +^\(*\)\{5}\s.*+ contains=stars
syntax match OL6 +^\(*\)\{6}\s.*+ contains=stars
syntax match OL7 +^\(*\)\{7}\s.*+ contains=stars
syntax match OL8 +^\(*\)\{8}\s.*+ contains=stars
syntax match OL9 +^\(*\)\{9}\s.*+ contains=stars
syntax match T1 +^\t*:.*$+ contains=tcolon,url 
syntax match T2 +^\t*;.*$+ contains=tcolon,url
syntax match T3 +^\t*|.*$+ contains=tcolon,url
syntax match T4 +^\t*>.*$+ contains=tcolon,url
hi T1 guifg=#00ee00
hi T2 guifg=#ffff33
hi T3 guifg=#99cc33
hi T4 guifg=#99cc66
"hi FoldColumn guifg=#666666 guibg=bg
syntax match tcolon '^\t*:' contained
hi tcolon guifg=#666666
syntax match url '<url:.*>'
hi url guifg=#888822

"syntax region Main start='^begin-org' end='^end-org' contains=orgPerl
let b:current_syntax = ''
unlet b:current_syntax

"syntax include @Vimcode $VIMRUNTIME\syntax\vim.vim
"syntax region orgVim start='^src-vimscript' end='^end-vimscript' contains=@Vimcode
"unlet b:current_syntax
"syntax include @Lispcode $VIMRUNTIME\syntax\lisp.vim
"syntax region orgLisp start='^#+begin-lisp' end='^#+end_src' contains=@Lispcode
syntax region orgLisp start='^#+begin_src\semacs-lisp' end='^#+end_src$' contains=@Lispcode
let b:current_syntax = 'combined'
hi orgLisp gui=bold

syntax region orgList start='^\s*\(\d\+[.):]\|[-+] \)' end='^\(\s*$\|^\*\)'me=e-1 

"unlet b:current_syntax
"syntax include @rinvim $VIMRUNTIME\syntax\r.vim
"syntax region orgR matchgroup=Snip start="^src-R" end="^end-R" keepend contains=@rinvim
"let b:current_syntax = ''
"unlet b:current_syntax
"syntax include @python $VIMRUNTIME\syntax\python.vim
"syntax region orgPython matchgroup=Snip start="^src-Python" end="^end-Python" keepend contains=@python
"hi link orgPython TabLineFill
"let b:current_syntax='combined'
"hi link Snip SpecialComment


" vim600: set foldmethod=marker foldlevel=0:

if &background == 'light'
	hi OL1 guifg=Blue ctermfg=DarkBlue
	hi OL2 guifg=Brown ctermfg=Brown
	hi OL3 guifg=DarkMagenta ctermfg=DarkMagenta
	hi OL4 guifg=DarkRed ctermfg=DarkRed
	hi OL5 guifg=DarkGray  	ctermfg=DarkGray
	hi OL6 guifg=DarkYellow 	ctermfg=DarkYellow
	hi OL7 guifg=Red  	ctermfg=Red
	hi OL8 guifg=DarkGreen	ctermfg=DarkGreen
	hi OL9 guifg=Magenta	ctermfg=Magenta
else
	hi OL1 guifg=#7744ff ctermfg=blue
	hi OL2 guifg=#aaaa22 ctermfg=brown
	hi OL3 guifg=#00ccff ctermfg=cyan
	hi OL4 guifg=#999999 gui=italic  	ctermfg=gray
	hi OL5 guifg=#eeaaee  	ctermfg=lightgray
	hi OL6 guifg=#9966ff 	ctermfg=yellow
	hi OL7 guifg=#dd99dd  	ctermfg=red
	hi OL8 guifg=cyan	ctermfg=grey
	hi OL9 guifg=magenta	ctermfg=blue
endif

hi Folded gui=bold guifg=#6633ff ctermfg=blue
"hi link OLB1 Folded 
hi WarningMsg gui=bold guifg=#aaaa22  ctermfg=brown
"hi link OLB2 WarningMsg
hi WildMenu gui=bold guifg=#00ccff  ctermfg=cyan
"hi link OLB3 WildMenu
hi DiffAdd gui=bold guifg=#999999 gui=italic  ctermfg=gray
"hi link OLB4 DiffAdd
hi DiffChange gui=bold guifg=#eeaaee  ctermfg=lightgray

hi OLB6 gui=bold guifg=#9966ff 	ctermfg=yellow
hi OLB7 gui=bold guifg=#dd99dd  	ctermfg=red
hi OLB8 gui=bold guifg=cyan	ctermfg=grey
hi OLB9 gui=bold guifg=magenta	ctermfg=blue

syn match Props '^\s*:\s*\S\+\s*:'
hi Props guifg=#ffa0a0
hi T1 guifg=#00ee00
hi T2 guifg=#ffff33
hi T3 guifg=#99cc33
hi T4 guifg=#99cc66

"hi code guifg=#88aa88 gui=bold
hi code guifg=orange gui=bold
syn match code '=\S.\{-}\S='
hi itals gui=italic guifg=#aaaaaa
syn match itals '/\zs\S.\{-}\S\ze/'
hi boldtext gui=bold guifg=#aaaaaa
syn match boldtext '*\zs\S.\{-}\S\ze\*'
hi undertext gui=underline guifg=#aaaaaa
syn match undertext '_\zs\S.\{-}\S\ze_'

syn match colon '^\t*:' contained
hi colon guifg=#666666
syn match lnumber '^\t*\(\d\.\)*\s\s' contained
hi lnumber guifg=#999999

if &background == "light"
	hi TODO guifg=Red gui=bold guibg=NONE ctermfg=Red cterm=bold ctermbg=NONE
	hi CANCELED guifg=Magenta gui=bold ctermfg=Magenta cterm=bold
	hi STARTED guifg=Brown gui=bold ctermfg=Brown cterm=bold
	hi NEXT guifg=DarkCyan gui=bold ctermfg=DarkCyan cterm=bold
	hi DONE guifg=SeaGreen gui=bold guibg=NONE ctermfg=DarkGreen cterm=bold ctermbg=NONE
else
	hi TODO guifg=Red gui=bold guibg=NONE ctermfg=Red cterm=bold ctermbg=NONE
	hi CANCELED guifg=Orange gui=bold ctermfg=Magenta cterm=bold
	hi STARTED guifg=Yellow gui=bold ctermfg=Yellow cterm=bold
	hi NEXT guifg=Cyan gui=bold ctermfg=Cyan cterm=bold
	hi DONE guifg=Green gui=bold guibg=NONE ctermfg=Green cterm=bold ctermbg=NONE
endif
