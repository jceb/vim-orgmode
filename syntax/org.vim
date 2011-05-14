" Heading
if !exists('g:org_heading_highlight_colors')
	let g:org_heading_highlight_colors = ['Title', 'Question', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']
endif

if !exists('g:org_heading_highlight_levels')
	let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
endif

if !exists('g:org_heading_shade_leading_stars')
	let g:org_heading_shade_leading_stars = 1
endif

let s:i = 1
let s:j = len(g:org_heading_highlight_colors)
let s:shade_stars = ''
if g:org_heading_shade_leading_stars == 1
	let s:shade_stars = ' contains=org_shade_stars'
	syntax match org_shade_stars /^\*\{2,\}/me=e-1 contained
	hi link org_shade_stars NonText
endif

while s:i <= g:org_heading_highlight_levels
	exec 'syntax match org_heading' . s:i . ' /^\*\{' . s:i . '\}\s.*/' . s:shade_stars
	exec 'hi link org_heading' . s:i . ' ' . g:org_heading_highlight_colors[(s:i - 1) % s:j]
	let s:i += 1
endwhile
unlet! s:i s:j s:shade_stars

" Todo keywords
if !exists('g:org_todo_keywords')
	let g:org_todo_keywords = ['TODO', '|', 'DONE']
endif

if !exists('g:org_todo_keyword_faces')
	let g:org_todo_keyword_faces = []
endif

let s:todo_headings = ''
let s:i = 1
while s:i <= g:org_heading_highlight_levels
	if s:todo_headings == ''
		let s:todo_headings = 'containedin=org_heading' . s:i
	else
		let s:todo_headings = s:todo_headings . ',org_heading' . s:i
	endif
	let s:i += 1
endwhile
unlet! s:i

let default_group = 'Todo'
for i in g:org_todo_keywords
	if i == '|'
		let default_group = 'Question'
		continue
	endif
	let group = default_group
	for j in g:org_todo_keyword_faces
		if j[0] == i
			let group = 'org_todo_keyword_face_' . i
			" TODO implement me
			exec 'hi ' . group . ExtendHI('Todo', '....')
			break
		endif
	endfor
	" TODO maybe using syntax keyword is better here
	exec 'syntax match org_todo_keyword_' . i . ' /\*\{1,\}\s\{1,\}\zs' . i .'/ ' . s:todo_headings
	exec 'hi link org_todo_keyword_' . i . ' ' . group
endfor
unlet! default_group s:todo_headings

" Propteries
syn region Error matchgroup=org_properties_delimiter start=/^\s*:PROPERTIES:\s*$/ end=/^\s*:END:\s*$/ contains=org_property keepend
syn match org_property /^\s*:[^\t :]\+:\s\+[^\t ]/ contained contains=org_property_value
syn match org_property_value /:\s\zs.*/ contained
hi link org_properties_delimiter Comment
hi link org_property Identifier
hi link org_property_value Statement

" Hyperlinks
syntax match hyperlink	"\[\{2}[^][]*\(\]\[[^][]*\)\?\]\{2}" contains=hyperlinkBracketsLeft,hyperlinkURL,hyperlinkBracketsRight containedin=ALL
syntax match hyperlinkBracketsLeft		contained "\[\{2}" conceal
syntax match hyperlinkURL				contained "[^][]*\]\[" conceal
syntax match hyperlinkBracketsRight		contained "\]\{2}" conceal

hi link hyperlink Underlined
