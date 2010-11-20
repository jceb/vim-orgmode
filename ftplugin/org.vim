" org.vim -- An implementation of Emacs org-mode in vim
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : GPL (see http://www.gnu.org/licenses/gpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Fri 19. Nov 2010 20:19:17 +0100 CET
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
	let g:orgmode_plugins = ['Navigator']
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
