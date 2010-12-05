" org.vim -- An implementation of Emacs org-mode in vim
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : GPL (see http://www.gnu.org/licenses/gpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Sat 04. Dec 2010 19:27:44 +0100 CET
" @Revision     : 0.1
" @vi           : ft=vim:tw=80:sw=4:ts=4
" 
" @Description  :
" @Usage        :
" @TODO         :
" @CHANGES      :

if &cp || exists("b:loaded_org")
    finish
endif
let b:loaded_org = 1

if ! exists('g:orgmode_plugins')
	let g:orgmode_plugins = ['Navigator', 'EditStructure']
endif

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

" taglist support for org-mode
if !exists('Tlist_Ctags_Cmd')
	finish
endif

" ****************** Options *******************************************
" How many title levels are supported, default is 3.
if !exists('Orgmode_Title_Level')
	let Orgmode_Title_Level = 3
endif

" When this file is reloaded, only load OrgmodeBrowser_Ctags_Cmd once.
if !exists('OrgmodeBrowser_Ctags_Cmd')
	let OrgmodeBrowser_Ctags_Cmd = Tlist_Ctags_Cmd
endif

" Orgmode tag definition start.
let s:OrgmodeBrowser_Config = ' --langdef=orgmode --langmap=orgmode:.org '

" Title tag definition
let s:OrgmodeBrowser_Config .= '--regex-orgmode="/^\*{1}\s+(.*)/\1/c,content/" '
if (Orgmode_Title_Level >= 2)
	let s:OrgmodeBrowser_Config .= '--regex-orgmode="/^(\*{2}\s+(.*)|\s{1}\*\s+(.*))/. \2/c,content/" '
endif
if (Orgmode_Title_Level >= 3)
	let s:OrgmodeBrowser_Config .= '--regex-orgmode="/^(\*{3}\s+(.*)|\s{2}\*\s+(.*))/.. \2/c,content/" '
endif
if (Orgmode_Title_Level >= 4)
	let s:OrgmodeBrowser_Config .= '--regex-orgmode="/^(\*{4}\s+(.*)|\s{3}\*\s+(.*))/... \2/c,content/" '
endif
if (Orgmode_Title_Level >= 5)
	let s:OrgmodeBrowser_Config .= '--regex-orgmode="/^(\*{5}\s+(.*)|\s{4}\*\s+(.*))/.... \2/c,content/" '
endif

" Pass parameters to taglist
let tlist_org_settings = 'orgmode;c:content'
let Tlist_Ctags_Cmd = OrgmodeBrowser_Ctags_Cmd . s:OrgmodeBrowser_Config
