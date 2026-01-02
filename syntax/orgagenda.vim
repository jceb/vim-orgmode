" TODO do we really need a separate syntax file for the agenda?
"      - Most of the stuff here is also in syntax.org
"      - DRY!

if exists("b:current_syntax")
    finish
endif

syn match org_todo_key /\[\zs[^]]*\ze\]/
hi def link org_todo_key Identifier

" Multi-colored tags in agenda
syn match org_tag_1 /:[a-iA-I][^: ]*:/hs=s+1,me=e-1
syn match org_tag_2 /:[j-rJ-R][^: ]*:/hs=s+1,me=e-1
syn match org_tag_3 /:[s-zS-Z0][^: ]*:/hs=s+1,me=e-1
syn match org_tag_4 /:[1-9_][^: ]*:/hs=s+1,me=e-1
syn match org_tag_5 /:[\W][^: ]*:/hs=s+1,me=e-1
hi def link org_tag_1 Title
hi def link org_tag_2 Constant
hi def link org_tag_3 Statement
hi def link org_tag_4 Type
hi def link org_tag_5 Special

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

if !exists('g:loaded_orgagenda_syntax')
	let g:loaded_orgagenda_syntax = 1
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
			" strip access key
			let l:_i = substitute(l:i, "\(.*$", "", "")

			let l:group = l:default_group
			for l:j in g:org_todo_keyword_faces
				if l:j[0] == l:_i
					let l:group = 'orgtodo_todo_keyword_face_' . l:_i
					call OrgExtendHighlightingGroup(l:default_group, l:group, OrgInterpretFaces(l:j[1]))
					break
				endif
			endfor
			silent! exec 'syntax match orgtodo_todo_keyword_' . l:_i . ' /' . l:_i .'/ ' . a:todo_headings
			silent! exec 'hi def link orgtodo_todo_keyword_' . l:_i . ' ' . l:group
		endfor
	endfunction
endif

call s:ReadTodoKeywords(g:org_todo_keywords, s:todo_headings)
unlet! s:todo_headings

" Timestamps
"<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \k\k\k>\)/
"<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \k\k\k \d\d:\d\d>\)/
"<2003-09-16 Tue 12:00-12:30>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \k\k\k \d\d:\d\d-\d\d:\d\d>\)/
"<2003-09-16 Tue>--<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \k\k\k>--<\d\d\d\d-\d\d-\d\d \k\k\k>\)/
"<2003-09-16 Tue 12:00>--<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \k\k\k \d\d:\d\d>--<\d\d\d\d-\d\d-\d\d \k\k\k \d\d:\d\d>\)/
syn match org_timestamp /\(<%%(diary-float.\+>\)/
hi def link org_timestamp PreProc

" special words
syn match today /TODAY$/
hi def link today PreProc

syn match week_agenda /^Week Agenda:$/
hi def link week_agenda PreProc

" Hyperlinks
syntax match hyperlink	"\[\{2}[^][]*\(\]\[[^][]*\)\?\]\{2}" contains=hyperlinkBracketsLeft,hyperlinkURL,hyperlinkBracketsRight containedin=ALL
syntax match hyperlinkBracketsLeft		contained "\[\{2}" conceal
syntax match hyperlinkURL				contained "[^][]*\]\[" conceal
syntax match hyperlinkBracketsRight		contained "\]\{2}" conceal
hi def link hyperlink Underlined

let b:current_syntax = "orgagenda"
