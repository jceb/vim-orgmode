" Headings
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
let s:contains = ' contains=org_timestamp,org_timestamp_inactive'
if g:org_heading_shade_leading_stars == 1
	let s:contains = s:contains . ',org_shade_stars'
	syntax match org_shade_stars /^\*\{2,\}/me=e-1 contained
	hi def link org_shade_stars NonText
else
	hi clear org_shade_stars
endif

while s:i <= g:org_heading_highlight_levels
	exec 'syntax match org_heading' . s:i . ' /^\*\{' . s:i . '\}\s.*/' . s:contains
	exec 'hi def link org_heading' . s:i . ' ' . g:org_heading_highlight_colors[(s:i - 1) % s:j]
	let s:i += 1
endwhile
unlet! s:i s:j s:contains

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
			exec 'hi def ' . group . ExtendHI('Todo', '....')
			break
		endif
	endfor
	exec 'syntax match org_todo_keyword_' . i . ' /\*\{1,\}\s\{1,\}\zs' . i .'/ ' . s:todo_headings
	exec 'hi def link org_todo_keyword_' . i . ' ' . group
endfor
unlet! default_group s:todo_headings

" Propteries
syn region Error matchgroup=org_properties_delimiter start=/^\s*:PROPERTIES:\s*$/ end=/^\s*:END:\s*$/ contains=org_property keepend
syn match org_property /^\s*:[^\t :]\+:\s\+[^\t ]/ contained contains=org_property_value
syn match org_property_value /:\s\zs.*/ contained
hi def link org_properties_delimiter PreProc
hi def link org_property Statement
hi def link org_property_value Constant

" Timestamps
syn match org_timestamp /\(<\d\{4\}-\d\{2\}-\d\{2\} .\+>\|<\d\{4\}-\d\{2\}-\d\{2\} .\+>--<\d\{4\}-\d\{2\}-\d\{2\} .\+>\|<%%(diary-float.\+>\)/
syn match org_timestamp_inactive /\(\[\d\{4\}-\d\{2\}-\d\{2\} .\+\]\|\[\d\{4\}-\d\{2\}-\d\{2\} .\+\]--\[\d\{4\}-\d\{2\}-\d\{2\} .\+\]\|\[%%(diary-float.\+\]\)/
hi def link org_timestamp PreProc
hi def link org_timestamp_inactive Comment

" Deadline/Schedule
syn match org_deadline_scheduled /^\s*\(DEADLINE\|SCHEDULED\):/
hi def link org_deadline_scheduled PreProc

" Tables
syn match org_table /^\s*|.*/ contains=org_timestamp,org_timestamp_inactive,hyperlink,org_table_separator,org_table_horizontal_line
syn match org_table_separator /\(^\s*|[-+]\+|\?\||\)/ contained
hi def link org_table_separator Type

" Hyperlinks
syntax match hyperlink	"\[\{2}[^][]*\(\]\[[^][]*\)\?\]\{2}" contains=hyperlinkBracketsLeft,hyperlinkURL,hyperlinkBracketsRight containedin=ALL
syntax match hyperlinkBracketsLeft		contained "\[\{2}" conceal
syntax match hyperlinkURL				contained "[^][]*\]\[" conceal
syntax match hyperlinkBracketsRight		contained "\]\{2}" conceal
hi def link hyperlink Underlined

" Comments
syntax match org_comment /^#.*/
hi def link org_comment Comment
