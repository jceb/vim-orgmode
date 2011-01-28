" org.vim -- An implementation of Emacs org-mode in vim
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : GPL (see http://www.gnu.org/licenses/gpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Fri 28. Jan 2011 17:59:16 +0100 CET
" @Revision     : 0.1
" @vi           : ft=vim:tw=80:sw=4:ts=4
" 
" @Description  :
" @Usage        :
" @TODO         :
" @CHANGES      :

" register keybindings if they don't have been registered before
if has('python') && exists("g:loaded_org") && ! exists("b:loaded_org")
	python ORGMODE.register_keybindings()
	let b:loaded_org = 1
	" default emacs settings
	setlocal shiftwidth=8
	setlocal tabstop=8
	setlocal comments-=s1:/*,mb:*,ex:*/
endif

" load plugin just once
if &cp || exists("g:loaded_org")
    finish
endif
let g:loaded_org = 1

" default emacs settings
setlocal shiftwidth=8
setlocal tabstop=8
setlocal comments-=s1:/*,mb:*,ex:*/

" display error message if python is not available
if ! has('python')
	echom 'Python not found, orgmode plugin not usable.'
	finish
endif

" general setting plugins that should be loaded and their order
if ! exists('g:org_plugins') && ! exists('b:org_plugins')
	let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Todo', 'TagsProperties', 'Misc']
endif

" make sure repeat plugin is load (or not)
try
	call repeat#set()
catch
endtry

" show and hide Org menu depending on the filetype
augroup orgmode
	au BufEnter		*		if &filetype == "org" | silent! python ORGMODE.register_menu() | endif
	au BufLeave		*		if &filetype == "org" | silent! python ORGMODE.unregister_menu() | endif
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
