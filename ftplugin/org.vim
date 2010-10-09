" org.vim -- An implementation of Emacs org-mode in vim
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : GPL (see http://www.gnu.org/licenses/gpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Fri 08. Oct 2010 23:00:56 +0200 CEST
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

let g:orgmode_plugins = ['Todo']

" Expand our path
python << EOF
import vim, os, sys

for p in vim.eval("&runtimepath").split(','):
   dname = p + os.path.sep + "ftplugin"
   if os.path.exists(dname + os.path.sep + "orgmode"):
      if dname not in sys.path:
         sys.path.append(dname)
      break

from orgmode import ORGMODE
EOF

nmap <leader>j :py ORGMODE.find_current_heading()<CR>
