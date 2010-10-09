"
" Script: syntax/outline.vim
"
" Version: 2.0
"
" Description:
"
"       This uses folding to mimic outline-mode in Emacs.  Set the filetype to
"       'outline' to activate this functinality.  Put it in the modeline to
"       preserve outlines between edits.  For example:
"
"               vim:set ft=outline:
"
" Installation:
"
"   Place this file in your home directory under ~/.vim/syntax/, or in the
"   system location under the syntax/ directory to provide it to all users.
"
" Maintainer: Tye Z. <zdro@yahoo.com>
"
" Customization:
"
"   The colors of the outline headers can be changed by linking them to
"   whatever you like.  For example:
"
"       hi! link Outline_1 Statement
"
" History:
"
"   Version 2.0:
"
"       - Rewritten to use syntax-folding instead of a fold expression
"       - Eliminated slowness in folds with large amounts of text
"
"   Version 1.2:
"
"       - Updated regexes for readability, using a number for the '*' count
"
"   Version 1.1:
"
"       - Initial version
"


"
" Do folding with syntax.  This works pretty darn well, and is simpler than a
" complicated foldexpr.
"
" - An outline block starts with a '*' and ends when approaching another '*'
"   at the beginning of a line.
"
" - An outline block can contain any outline block of a lower level.  So, a
"   level 3 can be inside a level 1 without the intermediary level 2.
"
" - A '_' can end a block, allowing one to insert extra space between two
"   folds.
"

syn region Outline_1 matchgroup=Outline_1_match
            \ start='^\*[^*].*$'
            \ end='\n\ze\n\?\*[^*]\|^<$'
            \ fold keepend

syn region Outline_2 matchgroup=Outline_2_match
            \ start='^\*\{2\}[^*].*$'
            \ end='\n\ze\n\?\*\{1,2\}[^*]\|^<\{2\}$'
            \ containedin=Outline_1,Outline_2
            \ fold keepend

syn region Outline_3 matchgroup=Outline_3_match
            \ start='^\*\{3\}[^*].*$'
            \ end='\n\ze\n\?\*\{1,3\}[^*]\|^<\{3\}$'
            \ containedin=Outline_1,Outline_2,Outline_3
            \ fold keepend

syn region Outline_4 matchgroup=Outline_4_match
            \ start='^\*\{4\}[^*].*$'
            \ end='\n\ze\n\?\*\{1,4\}[^*]\|^<\{4\}$'
            \ containedin=Outline_1,Outline_2,Outline_3,Outline_4
            \ fold keepend



""" Debugging: Hilight the whole block so we can see exactly what is being
"""            done.
"hi Outline_1 guibg=gray40
"hi Outline_2 guibg=#330000
"hi Outline_3 guibg=#003300
"hi Outline_4 guibg=#000033
"" Disable
""hi Outline_1 guibg=bg
""hi Outline_2 guibg=bg
""hi Outline_3 guibg=bg
""hi Outline_4 guibg=bg

hi! default link Outline_1_match Comment
hi! default link Outline_2_match Identifier
hi! default link Outline_3_match PreProc
hi! default link Outline_4_match Type

syn sync fromstart
setlocal fdm=syntax

finish

