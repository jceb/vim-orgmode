" Variables With Default Settings:
"
" Define the highlighting colors/group names for headings
" let g:org_heading_highlight_colors = ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']
"
" Definie the number of level of highlighting. If this number is bigger than
" the length of g:org_heading_highlight_colors the colors of
" g:org_heading_highlight_colors are repeated
" let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
"
" Defines if leading stars are displayed in the color of the heading or if a
" special NonText highlighting is used that hides them from user
" let g:org_heading_shade_leading_stars = 1
"
" Defines the keywords that are highlighted in headings. For more information
" about this variable, please consult the org-mode documentation
" (http://orgmode.org/org.html#index-org_002dtodo_002dkeywords-511)
" let g:org_todo_keywords = ['TODO', '|', 'DONE']
"
" Defines special faces (styles) for displaying g:org_todo_keywords. Please
" refer to vim documentation (topic |attr-list|) for allowed values for
" :weight, :slant, :decoration. Muliple colors can be separated by comma for
" :foreground and :background faces to provide different colors for gui and
" terminal mode.
" let g:org_todo_keyword_faces = []
"
" Examples:
"
" Define an additionaly keyword 'WAITING' and set the foreground color to
" 'cyan'. Define another keyword 'CANCELED' and set the foreground color to
" red, background to black and the weight to normal, slant to italc and
" decoration to underline
" let g:org_todo_keywords = [['TODO', 'WAITING', '|', 'DONE'], ['|', 'CANCELED']]
" let g:org_todo_keyword_faces = [['WAITING', 'cyan'], ['CANCELED', [':foreground red', ':background black', ':weight bold', ':slant italic', ':decoration underline']]]

" Headings
if !exists('g:org_heading_highlight_colors')
	let g:org_heading_highlight_colors = ['Title', 'Constant', 'Identifier', 'Statement', 'PreProc', 'Type', 'Special']
endif

if !exists('g:org_heading_highlight_levels')
	let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
endif

if !exists('g:org_heading_shade_leading_stars')
	let g:org_heading_shade_leading_stars = 1
endif

unlet! s:i s:j s:contains
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

if !exists('g:loaded_org_syntax')
	let g:loaded_org_syntax = 1

	function! s:ExtendHighlightingGroup(base_group, new_group, settings)
		let l:base_hi = ''
		redir => l:base_hi
		silent execute 'highlight ' . a:base_group
		redir END
		let l:group_hi = substitute(split(l:base_hi, '\n')[0], '^' . a:base_group . '\s\+xxx', '', '')
		execute 'highlight ' . a:new_group . l:group_hi . ' ' . a:settings
	endfunction

	function! s:InterpretFaces(faces)
		let l:res_faces = ''
		if type(a:faces) == 3
			let l:style = []
			for l:f in a:faces
				let l:_f = [l:f]
				if type(l:f) == 3
					let l:_f = l:f
				endif
				for l:g in l:_f
					if type(l:g) == 1 && l:g =~ '^:'
						if l:g !~ '[\t ]'
							continue
						endif
						let l:k_v = split(l:g)
						if l:k_v[0] == ':foreground'
							let l:gui_color = ''
							let l:found_gui_color = 0
							for l:color in split(l:k_v[1], ',')
								if l:color =~ '^#'
									let l:found_gui_color = 1
									let l:res_faces = l:res_faces . ' guifg=' . l:color
								elseif l:color != ''
									let l:gui_color = l:color
									let l:res_faces = l:res_faces . ' ctermfg=' . l:color
								endif
							endfor
							if ! l:found_gui_color && l:gui_color != ''
								let l:res_faces = l:res_faces . ' guifg=' . l:gui_color
							endif
						elseif l:k_v[0] == ':background'
							let l:gui_color = ''
							let l:found_gui_color = 0
							for l:color in split(l:k_v[1], ',')
								if l:color =~ '^#'
									let l:found_gui_color = 1
									let l:res_faces = l:res_faces . ' guibg=' . l:color
								elseif l:color != ''
									let l:gui_color = l:color
									let l:res_faces = l:res_faces . ' ctermbg=' . l:color
								endif
							endfor
							if ! l:found_gui_color && l:gui_color != ''
								let l:res_faces = l:res_faces . ' guibg=' . l:gui_color
							endif
						elseif l:k_v[0] == ':weight' || l:k_v[0] == ':slant' || l:k_v[0] == ':decoration'
							if index(l:style, l:k_v[1]) == -1
								call add(l:style, l:k_v[1])
							endif
						endif
					elseif type(l:g) == 1
						" TODO emacs interprets the color and automatically determines
						" whether it should be set as foreground or background color
						let l:res_faces = l:res_faces . ' ctermfg=' . l:k_v[1] . ' guifg=' . l:k_v[1]
					endif
				endfor
			endfor
			let l:s = ''
			for l:i in l:style
				if l:s == ''
					let l:s = l:i
				else
					let l:s = l:s . ','. l:i
				endif
			endfor
			if l:s != ''
				let l:res_faces = l:res_faces . ' term=' . l:s . ' cterm=' . l:s . ' gui=' . l:s
			endif
		elseif type(a:faces) == 1
			" TODO emacs interprets the color and automatically determines
			" whether it should be set as foreground or background color
			let l:res_faces = l:res_faces . ' ctermfg=' . a:faces . ' guifg=' . a:faces
		endif
		return l:res_faces
	endfunction

	function! s:ReadTodoKeywords(keywords, todo_headings)
		let l:default_group = 'Todo'
		for l:i in a:keywords
			if type(l:i) == 3
				call s:ReadTodoKeywords(l:i, a:todo_headings)
				continue
			endif
			if l:i == '|'
				let l:default_group = 'Question'
				continue
			endif
			let l:group = l:default_group
			for l:j in g:org_todo_keyword_faces
				if l:j[0] == l:i
					let l:group = 'org_todo_keyword_face_' . l:i
					call s:ExtendHighlightingGroup(l:default_group, l:group, s:InterpretFaces(l:j[1]))
					break
				endif
			endfor
			exec 'syntax match org_todo_keyword_' . l:i . ' /\*\{1,\}\s\{1,\}\zs' . l:i .'/ ' . a:todo_headings
			exec 'hi def link org_todo_keyword_' . l:i . ' ' . l:group
		endfor
	endfunction
endif

call s:ReadTodoKeywords(g:org_todo_keywords, s:todo_headings)
unlet! s:todo_headings

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
