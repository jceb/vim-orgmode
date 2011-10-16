" org.vim -- Text outlining and task management for Vim based on Emacs' Org-Mode
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : AGPL3 (see http://www.gnu.org/licenses/agpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Tue 13. Sep 2011 20:52:57 +0200 CEST
" @Revision     : 0.4
" @vi           : ft=vim:tw=80:sw=4:ts=4

if ! has('python') || v:version < 703
	echoerr "Unable to start orgmode. Orgmode depends on Vim >= 7.3 with Python support complied in."
	finish
endif

if ! exists("b:did_ftplugin")
	" default emacs settings
	setlocal comments-=s1:/*,mb:*,ex:*/ conceallevel=2 concealcursor=nc tabstop=8 shiftwidth=8 commentstring=#\ %s

	" register keybindings if they don't have been registered before
	if exists("g:loaded_org")
		python ORGMODE.register_keybindings()
	endif
endif

" load plugin just once
if &cp || exists("g:loaded_org")
    finish
endif
let g:loaded_org = 1

" general setting plugins that should be loaded and their order
if ! exists('g:org_plugins') && ! exists('b:org_plugins')
	let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Hyperlinks', '|', 'Todo', 'TagsProperties', 'Date', 'Agenda', 'Misc', '|', 'Export']
endif

if ! exists('g:org_syntax_highlight_leading_stars') && ! exists('b:org_syntax_highlight_leading_stars')
	let g:org_syntax_highlight_leading_stars = 1
endif


" make sure repeat plugin is load (or not)
try
	call repeat#set()
catch
endtry

function! <SID>OrgRegisterMenu()
	python ORGMODE.register_menu()
endfunction

function! <SID>OrgUnregisterMenu()
	python ORGMODE.unregister_menu()
endfunction

function! <SID>OrgDeleteUnusedDocument(bufnr)
python << EOF
b = int(vim.eval('a:bufnr'))
if b in ORGMODE._documents:
	del ORGMODE._documents[b]
EOF
endfunction

" show and hide Org menu depending on the filetype
augroup orgmode
	au BufEnter		*		:if &filetype == "org" | call <SID>OrgRegisterMenu() | endif
	au BufLeave		*		:if &filetype == "org" | call <SID>OrgUnregisterMenu() | endif
	au BufDelete	*		:call <SID>OrgDeleteUnusedDocument(expand('<abuf>'))
augroup END

" Expand our path
python << EOF
import vim, os, sys

for p in vim.eval("&runtimepath").split(','):
	dname = os.path.join(p, "ftplugin")
	if os.path.exists(os.path.join(dname, "orgmode")):
		if dname not in sys.path:
			sys.path.append(dname)
			break

from orgmode import ORGMODE
ORGMODE.start()
EOF

" ******************** Taglist/Tagbar integration ********************

" tag-bar support for org-mode
let g:tagbar_type_org = {
			\ 'ctagstype' : 'org',
			\ 'kinds'     : [
				\ 's:sections',
				\ 'h:hyperlinks',
			\ ],
			\ 'sort'    : 0,
			\ 'deffile' : expand('<sfile>:p:h') . '/org.cnf'
			\ }

" taglist support for org-mode
if !exists('g:Tlist_Ctags_Cmd')
	finish
endif

" Pass parameters to taglist
let g:tlist_org_settings = 'org;s:section;h:hyperlinks'
let g:Tlist_Ctags_Cmd .= ' --options=' . expand('<sfile>:p:h') . '/org.cnf '
