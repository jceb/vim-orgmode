" org.vim -- An implementation of Emacs org-mode in vim
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : GPL (see http://www.gnu.org/licenses/gpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Mon 04. Apr 2011 21:01:07 +0200 CEST
" @Revision     : 0.1
" @vi           : ft=vim:tw=80:sw=4:ts=4
"
" @Description  :
" @Usage        :
" @TODO         :
" @CHANGES      :

if ! exists("b:did_ftplugin")
	" default emacs settings
	setlocal comments-=s1:/*,mb:*,ex:*/ cole=2 cocu=nc tabstop=8 shiftwidth=8

	" register keybindings if they don't have been registered before
	if has('python') && exists("g:loaded_org")
		python ORGMODE.register_keybindings()
	endif
endif

" load plugin just once
if &cp || exists("g:loaded_org")
    finish
endif
let g:loaded_org = 1

" display error message if python is not available
if ! has('python')
	echom 'Python not found, orgmode plugin is not usable.'
	finish
endif

" general setting plugins that should be loaded and their order
if ! exists('g:org_plugins') && ! exists('b:org_plugins')
	let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Misc']
	"let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Hyperlinks', '|', 'Todo', 'TagsProperties', 'Date', 'LoggingWork', 'Misc']
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

" show and hide Org menu depending on the filetype
augroup orgmode
	au BufEnter		*		:if &filetype == "org" | call <SID>OrgRegisterMenu() | endif
	au BufLeave		*		:if &filetype == "org" | call <SID>OrgUnregisterMenu() | endif
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

" ******************** Taglist integration ********************

" taglist support for org-mode
if !exists('Tlist_Ctags_Cmd')
	finish
endif

" How many title levels are supported, default is 3.
if !exists('g:org_taglist_level')
	let g:org_taglist_level = 3
endif

" Orgmode tag definition start.
let s:org_taglist_config = ' --langdef=orgmode --langmap=orgmode:.org '

" Title tag definition
let i = 1
let j = ''
while i <= g:org_taglist_level
	let s:org_taglist_config .= '--regex-orgmode="/^(\*{'.i.'}\s+(.*)|\s{1}\*\s+(.*))/'.j.'\2/c,content/" '

	if i == 1
		let j = '. '
	else
		let j = '.'.j
	endif

	let i = i + 1
endwhile

" Pass parameters to taglist
let tlist_org_settings = 'orgmode;c:content'
let Tlist_Ctags_Cmd .= s:org_taglist_config
