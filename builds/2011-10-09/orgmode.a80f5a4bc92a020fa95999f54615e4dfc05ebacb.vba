" Vimball Archiver by Charles E. Campbell, Jr., Ph.D.
UseVimball
finish
ftdetect/org.vim	[[[1
2
autocmd BufNewFile,BufReadPost *.org setfiletype org
"autocmd BufNewFile,BufReadPost org:todo* setfiletype orgtodo
syntax/orgtodo.vim	[[[1
47
syn match org_todo_key /\[\zs[^]]*\ze\]/
hi def link org_todo_key Identifier

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

if !exists('g:loaded_orgtodo_syntax')
	let g:loaded_orgtodo_syntax = 1
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
			exec 'syntax match orgtodo_todo_keyword_' . l:_i . ' /' . l:_i .'/ ' . a:todo_headings
			exec 'hi def link orgtodo_todo_keyword_' . l:_i . ' ' . l:group
		endfor
	endfunction
endif

call s:ReadTodoKeywords(g:org_todo_keywords, s:todo_headings)
unlet! s:todo_headings
syntax/org.vim	[[[1
232
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

	function! OrgExtendHighlightingGroup(base_group, new_group, settings)
		let l:base_hi = ''
		redir => l:base_hi
		silent execute 'highlight ' . a:base_group
		redir END
		let l:group_hi = substitute(split(l:base_hi, '\n')[0], '^' . a:base_group . '\s\+xxx', '', '')
		execute 'highlight ' . a:new_group . l:group_hi . ' ' . a:settings
	endfunction

	function! OrgInterpretFaces(faces)
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
			" strip access key
			let l:_i = substitute(l:i, "\(.*$", "", "")

			let l:group = l:default_group
			for l:j in g:org_todo_keyword_faces
				if l:j[0] == l:_i
					let l:group = 'org_todo_keyword_face_' . l:_i
					call OrgExtendHighlightingGroup(l:default_group, l:group, OrgInterpretFaces(l:j[1]))
					break
				endif
			endfor
			exec 'syntax match org_todo_keyword_' . l:_i . ' /\*\{1,\}\s\{1,\}\zs' . l:_i .'/ ' . a:todo_headings
			exec 'hi def link org_todo_keyword_' . l:_i . ' ' . l:group
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
"<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a>\)/
"<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>\)/
"<2003-09-16 Tue 12:00-12:30>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d-\d\d:\d\d>\)/

"<2003-09-16 Tue>--<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a>--<\d\d\d\d-\d\d-\d\d \a\a\a>\)/
"<2003-09-16 Tue 12:00>--<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>--<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>\)/
syn match org_timestamp /\(<%%(diary-float.\+>\)/

"[2003-09-16 Tue]
syn match org_timestamp_inactive /\(\[\d\d\d\d-\d\d-\d\d \a\a\a\]\)/
"[2003-09-16 Tue 12:00]
syn match org_timestamp_inactive /\(\[\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d\]\)/

"[2003-09-16 Tue]--[2003-09-16 Tue]
syn match org_timestamp_inactive /\(\[\d\d\d\d-\d\d-\d\d \a\a\a\]--\[\d\d\d\d-\d\d-\d\d \a\a\a\]\)/
"[2003-09-16 Tue 12:00]--[2003-09-16 Tue 12:00]
syn match org_timestamp_inactive /\(\[\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d\]--\[\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d\]\)/
syn match org_timestamp_inactive /\(\[%%(diary-float.\+\]\)/

hi def link org_timestamp PreProc
hi def link org_timestamp_inactive Comment

" Lists
let s:listLeader = "^\\s*[\\+*-]\\s*"
exec "syn match org_list_description /".s:listLeader."\\zs.\\{-}\\ze ::/"
hi def link org_list_description Identifier

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
syntax/orgagenda.vim	[[[1
75
syn match org_todo_key /\[\zs[^]]*\ze\]/
hi def link org_todo_key Identifier

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
			exec 'syntax match orgtodo_todo_keyword_' . l:_i . ' /' . l:_i .'/ ' . a:todo_headings
			exec 'hi def link orgtodo_todo_keyword_' . l:_i . ' ' . l:group
		endfor
	endfunction
endif

call s:ReadTodoKeywords(g:org_todo_keywords, s:todo_headings)
unlet! s:todo_headings

" Timestamps
"<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a>\)/
"<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>\)/
"<2003-09-16 Tue 12:00-12:30>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d-\d\d:\d\d>\)/
"<2003-09-16 Tue>--<2003-09-16 Tue>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a>--<\d\d\d\d-\d\d-\d\d \a\a\a>\)/
"<2003-09-16 Tue 12:00>--<2003-09-16 Tue 12:00>
syn match org_timestamp /\(<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>--<\d\d\d\d-\d\d-\d\d \a\a\a \d\d:\d\d>\)/
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
ftplugin/org.cnf	[[[1
5
--langdef=org
--langmap=org:.org
--regex-org=/^(\*+)[[:space:]]+(.*)([[:space:]]+:[^\t ]*:)?$/\1 \2/s,sections/
--regex-org=/\[\[([^][]+)\]\]/\1/h,hyperlinks/
--regex-org=/\[\[[^][]+\]\[([^][]+)\]\]/\1/h,hyperlinks/
ftplugin/orgmode/keybinding.py	[[[1
210
# -*- coding: utf-8 -*-

import vim

MODE_ALL = u'a'
MODE_NORMAL = u'n'
MODE_VISUAL = u'v'
MODE_INSERT = u'i'
MODE_OPERATOR = u'o'

OPTION_BUFFER_ONLY = u'<buffer>'
OPTION_SLIENT = u'<silent>'

def _register(f, name):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		if hasattr(p, name) and isinstance(getattr(p, name), list):
			for i in getattr(p, name):
				i.create()
		return p
	return r

def register_keybindings(f):
	return _register(f, u'keybindings')

def register_commands(f):
	return _register(f, u'commands')

class Command(object):
	u""" A vim command """

	def __init__(self, name, command, arguments=u'0', complete=None, overwrite_exisiting=False):
		u"""
		:name:		The name of command, first character must be uppercase
		:command:	The actual command that is executed
		:arguments:	See :h :command-nargs, only the arguments need to be specified
		:complete:	See :h :command-completion, only the completion arguments need to be specified
		"""
		object.__init__(self)

		self._name                = name
		self._command             = command
		self._arguments           = arguments
		self._complete            = complete
		self._overwrite_exisiting = overwrite_exisiting

	def __unicode__(self):
		return u':%s<CR>' % self.name

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	@property
	def name(self):
		return self._name

	@property
	def command(self):
		return self._command

	@property
	def arguments(self):
		return self._arguments

	@property
	def complete(self):
		return self._complete

	@property
	def overwrite_exisiting(self):
		return self._overwrite_exisiting

	def create(self):
		u""" Register/create the command
		"""
		vim.command((':command%(overwrite)s -nargs=%(arguments)s %(complete)s %(name)s %(command)s' %
				{u'overwrite': '!' if self.overwrite_exisiting else '',
					u'arguments': self.arguments.encode(u'utf-8'),
					u'complete': '-complete=%s' % self.complete.encode(u'utf-8') if self.complete else '',
					u'name': self.name,
					u'command': self.command}
				).encode(u'utf-8'))

class Plug(object):
	u""" Represents a <Plug> to an abitrary command """

	def __init__(self, name, command, mode=MODE_NORMAL):
		u"""
		:name: the name of the <Plug> should be ScriptnameCommandname
		:command: the actual command
		"""
		object.__init__(self)

		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR')
		self._mode = mode

		self.name = name
		self.command = command
		self.created = False

	def __unicode__(self):
		return u'<Plug>%s' % self.name

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def create(self):
		if not self.created:
			self.created = True
			cmd = self._mode
			if cmd == MODE_ALL:
				cmd = u''
			vim.command((u':%snoremap %s %s' % (cmd, str(self), self.command)).encode(u'utf-8'))

	@property
	def mode(self):
		return self._mode

class Keybinding(object):
	u""" Representation of a single key binding """

	def __init__(self, key, action, mode=None, options=None, remap=True, buffer_only=True, silent=True):
		u"""
		:key: the key(s) action is bound to
		:action: the action triggered by key(s)
		:mode: definition in which vim modes the key binding is valid. Should be one of MODE_*
		:option: list of other options like <silent>, <buffer> ...
		:repmap: allow or disallow nested mapping
		:buffer_only: define the key binding only for the current buffer
		"""
		object.__init__(self)
		self._key = key
		self._action = action

		# grab mode from plug if not set otherwise
		if isinstance(self._action, Plug) and not mode:
			mode = self._action.mode

		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR')
		self._mode = mode
		self._options = options
		if self._options is None:
			self._options = []
		self._remap = remap
		self._buffer_only = buffer_only
		self._silent = silent

		if self._buffer_only and OPTION_BUFFER_ONLY not in self._options:
			self._options.append(OPTION_BUFFER_ONLY)

		if self._silent and OPTION_SLIENT not in self._options:
			self._options.append(OPTION_SLIENT)

	@property
	def key(self):
		return self._key

	@property
	def action(self):
		return str(self._action)

	@property
	def mode(self):
		return self._mode

	@property
	def options(self):
		return self._options[:]

	@property
	def remap(self):
		return self._remap

	@property
	def buffer_only(self):
		return self._buffer_only

	@property
	def silent(self):
		return self._silent

	def create(self):
		from orgmode import ORGMODE, echom

		cmd = self._mode
		if cmd == MODE_ALL:
			cmd = u''
		if not self._remap:
			cmd += u'nore'
		try:
			create_mapping = True
			if isinstance(self._action, Plug):
				# create plug
				self._action.create()
				if int(vim.eval((u'hasmapto("%s")' % (self._action, )).encode(u'utf-8'))):
					create_mapping = False
			if isinstance(self._action, Command):
				# create command
				self._action.create()

			if create_mapping:
				vim.command((u':%smap %s %s %s' % (cmd, u' '.join(self._options), self._key, self._action)).encode(u'utf-8'))
		except Exception, e:
			if ORGMODE.debug:
				echom(u'Failed to register key binding %s %s' % (self._key, self._action))


# vim: set noexpandtab:
ftplugin/orgmode/menu.py	[[[1
150
# -*- coding: utf-8 -*-

import vim

from orgmode.keybinding import Keybinding, MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT

def register_menu(f):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		def create(entry):
			if isinstance(entry, Submenu) or isinstance(entry, Separator) \
					or isinstance(entry, ActionEntry):
				entry.create()

		if hasattr(p, u'menu'):
			if isinstance(p.menu, list) or isinstance(p.menu, tuple):
				for e in p.menu:
					create(e)
			else:
				create(p.menu)
		return p
	return r

class Submenu(object):
	u""" Submenu entry """

	def __init__(self, name, parent=None):
		object.__init__(self)
		self.name = name
		self.parent = parent
		self._children = []

	def __add__(self, entry):
		if entry not in self._children:
			self._children.append(entry)
			entry.parent = self
			return entry

	def __sub__(self, entry):
		if entry in self._children:
			idx = self._children.index(entry)
			del self._children[idx]

	@property
	def children(self):
		return self._children[:]

	def get_menu(self):
		n = self.name.replace(u' ', u'\\ ')
		if self.parent:
			return u'%s.%s' % (self.parent.get_menu(), n)
		return n

	def create(self):
		for c in self.children:
			c.create()

	def __str__(self):
		res = self.name
		for c in self.children:
			res += str(c)
		return res

class Separator(object):
	u""" Menu entry for a Separator """

	def __init__(self, parent=None):
		object.__init__(self)
		self.parent = parent

	def __unicode__(self):
		return u'-----'

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def create(self):
		if self.parent:
			menu = self.parent.get_menu()
			vim.command((u'menu %s.-%s- :' % (menu, id(self))).encode(u'utf-8'))

class ActionEntry(object):
	u""" ActionEntry entry """

	def __init__(self, lname, action, rname=None, mode=MODE_NORMAL, parent=None):
		u"""
		:lname: menu title on the left hand side of the menu entry
		:action: could be a vim command sequence or an actual Keybinding
		:rname: menu title that appears on the right hand side of the menu
				entry. If action is a Keybinding this value ignored and is
				taken from the Keybinding
		:mode: defines when the menu entry/action is executable
		:parent: the parent instance of this object. The only valid parent is Submenu
		"""
		object.__init__(self)
		self._lname = lname
		self._action = action
		self._rname = rname
		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT')
		self._mode = mode
		self.parent = parent

	def __str__(self):
		return u'%s\t%s' % (self.lname, self.rname)

	@property
	def lname(self):
		return self._lname.replace(u' ', u'\\ ')

	@property
	def action(self):
		if isinstance(self._action, Keybinding):
			return self._action.action
		return self._action

	@property
	def rname(self):
		if isinstance(self._action, Keybinding):
			return self._action.key.replace(u'<Tab>', u'Tab')
		return self._rname

	@property
	def mode(self):
		if isinstance(self._action, Keybinding):
			return self._action.mode
		return self._mode

	def create(self):
		menucmd = u':%smenu ' % self.mode
		menu = u''
		cmd = u''

		if self.parent:
			menu = self.parent.get_menu()
		menu += u'.%s' % self.lname

		if self.rname:
			cmd = u'%s %s<Tab>%s %s' % (menucmd, menu, self.rname, self.action)
		else:
			cmd = u'%s %s %s' % (menucmd, menu, self.action)

		vim.command(cmd.encode(u'utf-8'))

		# keybindings should be stored in the plugin.keybindings property and be registered by the appropriate keybinding registrar
		#if isinstance(self._action, Keybinding):
		#	self._action.create()


# vim: set noexpandtab:
ftplugin/orgmode/__init__.py	[[[1
374
# -*- coding: utf-8 -*-

"""
	VIM ORGMODE
	~~~~~~~~~~~~

	TODO
"""

import imp
import types

import vim

import orgmode.keybinding
import orgmode.menu
import orgmode.plugins
import orgmode.settings
from orgmode.exceptions import PluginError
from orgmode.vimbuffer import VimBuffer
from orgmode.liborgmode.agenda import AgendaManager


REPEAT_EXISTS = bool(int(vim.eval('exists("*repeat#set()")')))
TAGSPROPERTIES_EXISTS = False


def realign_tags(f):
	u"""
	Update tag alignment, dependency to TagsProperties plugin!
	"""
	def r(*args, **kwargs):
		global TAGSPROPERTIES_EXISTS
		res = f(*args, **kwargs)

		if not TAGSPROPERTIES_EXISTS and u'TagsProperties' in ORGMODE.plugins:
			TAGSPROPERTIES_EXISTS = True

		if TAGSPROPERTIES_EXISTS:
			ORGMODE.plugins[u'TagsProperties'].realign_tags()

		return res
	return r


def repeat(f):
	u"""
	Integrate with the repeat plugin if available

	The decorated function must return the name of the <Plug> command to
	execute by the repeat plugin.
	"""
	def r(*args, **kwargs):
		res = f(*args, **kwargs)
		if REPEAT_EXISTS and isinstance(res, basestring):
			vim.command((u'silent! call repeat#set("\\<Plug>%s")' % res)
					.encode(u'utf-8'))
		return res
	return r


def apply_count(f):
	u"""
	Decorator which executes function v:count or v:prevount (not implemented,
	yet) times. The decorated function must return a value that evaluates to
	True otherwise the function is not repeated.
	"""
	def r(*args, **kwargs):
		count = 0
		try:
			count = int(vim.eval(u'v:count'.encode('utf-8')))

			# visual count is not implemented yet
			#if not count:
			#	count = int(vim.eval(u'v:prevcount'.encode(u'utf-8')))
		except Exception, e:
			pass

		res = f(*args, **kwargs)
		count -= 1
		while res and count > 0:
			f(*args, **kwargs)
			count -= 1
		return res
	return r


def echo(message):
	u"""
	Print a regular message that will not be visible to the user when
	multiple lines are printed
	"""
	vim.command((u':echo "%s"' % message).encode(u'utf-8'))


def echom(message):
	u"""
	Print a regular message that will be visible to the user, even when
	multiple lines are printed
	"""
	# probably some escaping is needed here
	vim.command((u':echomsg "%s"' % message).encode(u'utf-8'))


def echoe(message):
	u"""
	Print an error message. This should only be used for serious errors!
	"""
	# probably some escaping is needed here
	vim.command((u':echoerr "%s"' % message).encode(u'utf-8'))


def insert_at_cursor(text, move=True, start_insertmode=False):
	u"""Insert text at the position of the cursor.

	If move==True move the cursor with the inserted text.
	"""
	d = ORGMODE.get_document(allow_dirty=True)
	line, col = vim.current.window.cursor
	_text = d._content[line - 1]
	d._content[line - 1] = _text[:col + 1] + text + _text[col + 1:]
	if move:
		vim.current.window.cursor = (line, col + len(text))
	if start_insertmode:
		vim.command(u'startinsert'.encode(u'utf-8'))


def get_user_input(message):
	u"""Print the message and take input from the user.
	Return the input or None if there is no input.
	"""
	vim.command(u'call inputsave()'.encode(u'utf-8'))
	vim.command((u"let user_input = input('" + message + u": ')")
			.encode(u'utf-8'))
	vim.command(u'call inputrestore()'.encode(u'utf-8'))
	try:
		return vim.eval(u'user_input'.encode(u'utf-8')).decode(u'utf-8')
	except:
		return None


def get_bufnumber(bufname):
	"""
	Return the number of the buffer for the given bufname if it exist;
	else None.
	"""
	for b in vim.buffers:
		if b.name == bufname:
			return int(b.number)


def get_bufname(bufnr):
	"""
	Return the name of the buffer for the given bufnr if it exist; else None.
	"""
	for b in vim.buffers:
		if b.number == bufnr:
			return b.name


def indent_orgmode():
	u""" Set the indent value for the current line in the variable
	b:indent_level

	Vim prerequisites:
		:setlocal indentexpr=Method-which-calls-indent_orgmode

	:returns: None
	"""
	line = int(vim.eval(u'v:lnum'.encode(u'utf-8')))
	d = ORGMODE.get_document()
	heading = d.current_heading(line - 1)
	if heading and line != heading.start_vim:
		vim.command((u'let b:indent_level = %d' % (heading.level + 1))
				.encode(u'utf-8'))


def fold_text(allow_dirty=False):
	u""" Set the fold text
		:setlocal foldtext=Method-which-calls-foldtext

	:allow_dirty:	Perform a query without (re)building the DOM if True
	:returns: None
	"""
	line = int(vim.eval(u'v:foldstart'.encode(u'utf-8')))
	d = ORGMODE.get_document(allow_dirty=allow_dirty)
	heading = None
	if allow_dirty:
		heading = d.find_current_heading(line - 1)
	else:
		heading = d.current_heading(line - 1)
	if heading:
		str_heading = unicode(heading)

		# expand tabs
		ts = int(vim.eval(u'&ts'.encode('utf-8')))
		idx = str_heading.find(u'\t')
		if idx != -1:
			tabs, spaces = divmod(idx, ts)
			str_heading = str_heading.replace(u'\t', u' ' * (ts - spaces), 1)
			str_heading = str_heading.replace(u'\t', u' ' * ts)

		# Workaround for vim.command seems to break the completion menu
		vim.eval((u'SetOrgFoldtext("%s")' % (str_heading.replace(
				u'\\', u'\\\\').replace(u'"', u'\\"'), )).encode(u'utf-8'))
		#vim.command((u'let b:foldtext = "%s... "' % \
		#		(str_heading.replace(u'\\', u'\\\\')
		#		.replace(u'"', u'\\"'), )).encode('utf-8'))


def fold_orgmode(allow_dirty=False):
	u""" Set the fold expression/value for the current line in the variable
	b:fold_expr

	Vim prerequisites:
		:setlocal foldmethod=expr
		:setlocal foldexpr=Method-which-calls-fold_orgmode

	:allow_dirty:	Perform a query without (re)building the DOM if True
	:returns: None
	"""
	line = int(vim.eval(u'v:lnum'.encode(u'utf-8')))
	d = ORGMODE.get_document(allow_dirty=allow_dirty)
	heading = None
	if allow_dirty:
		heading = d.find_current_heading(line - 1)
	else:
		heading = d.current_heading(line - 1)
	if heading:
		if line == heading.start_vim:
			vim.command((u'let b:fold_expr = ">%d"' % heading.level).encode(u'utf-8'))
		#elif line == heading.end_vim:
		#	vim.command((u'let b:fold_expr = "<%d"' % heading.level).encode(u'utf-8'))
		# end_of_last_child_vim is a performance junky and is actually not needed
		#elif line == heading.end_of_last_child_vim:
		#	vim.command((u'let b:fold_expr = "<%d"' % heading.level).encode(u'utf-8'))
		else:
			vim.command((u'let b:fold_expr = %d' % heading.level).encode(u'utf-8'))


class OrgMode(object):
	u""" Vim Buffer """

	def __init__(self):
		object.__init__(self)
		self.debug = bool(int(orgmode.settings.get(u'org_debug', False)))

		self.orgmenu = orgmode.menu.Submenu(u'&Org')
		self._plugins = {}
		# list of vim buffer objects
		self._documents = {}

		# agenda manager
		self.agenda_manager = AgendaManager()

	def get_document(self, bufnr=0, allow_dirty=False):
		""" Retrieve instance of vim buffer document. This Document should be
		used for manipulating the vim buffer.

		:bufnr:			Retrieve document with bufnr
		:allow_dirty:	Allow the retrieved document to be dirty

		:returns:	vim buffer instance
		"""
		if bufnr == 0:
			bufnr = vim.current.buffer.number

		if bufnr in self._documents:
			if allow_dirty or self._documents[bufnr].is_insync:
				return self._documents[bufnr]
		self._documents[bufnr] = VimBuffer(bufnr).init_dom()
		return self._documents[bufnr]

	@property
	def plugins(self):
		return self._plugins.copy()

	@orgmode.keybinding.register_keybindings
	@orgmode.keybinding.register_commands
	@orgmode.menu.register_menu
	def register_plugin(self, plugin):
		if not isinstance(plugin, basestring):
			raise ValueError(u'Parameter plugin is not of type string')

		if plugin == u'|':
			self.orgmenu + orgmode.menu.Separator()
			self.orgmenu.children[-1].create()
			return

		if plugin in self._plugins:
			raise PluginError(u'Plugin %s has already been loaded')

		# a python module
		module = None

		# actual plugin class
		_class = None

		# locate module and initialize plugin class
		try:
			module = imp.find_module(plugin, orgmode.plugins.__path__)
		except ImportError, e:
			echom(u'Plugin not found: %s' % plugin)
			if self.debug:
				raise e
			return

		if not module:
			echom(u'Plugin not found: %s' % plugin)
			return

		try:
			module = imp.load_module(plugin, *module)
			if not hasattr(module, plugin):
				echoe(u'Unable to find plugin: %s' % plugin)
				if self.debug:
					raise PluginError(u'Unable to find class %s' % plugin)
				return
			_class = getattr(module, plugin)
			self._plugins[plugin] = _class()
			self._plugins[plugin].register()
			if self.debug:
				echo(u'Plugin registered: %s' % plugin)
			return self._plugins[plugin]
		except Exception, e:
			echoe(u'Unable to activate plugin: %s' % plugin)
			if self.debug:
				import traceback
				echoe(traceback.format_exc())

	def register_keybindings(self):
		@orgmode.keybinding.register_keybindings
		def dummy(plugin):
			return plugin

		for p in self.plugins.itervalues():
			dummy(p)

	def register_menu(self):
		self.orgmenu.create()

	def unregister_menu(self):
		vim.command(u'silent! aunmenu Org'.encode(u'utf-8'))

	def start(self):
		u""" Start orgmode and load all requested plugins
		"""
		plugins = orgmode.settings.get(u"org_plugins")

		if not plugins:
			echom(u'orgmode: No plugins registered.')

		if isinstance(plugins, basestring):
			try:
				self.register_plugin(plugins)
			except Exception, e:
				import traceback
				traceback.print_exc()
		elif isinstance(plugins, types.ListType) or \
				isinstance(plugins, types.TupleType):
			for p in plugins:
				try:
					self.register_plugin(p)
				except Exception, e:
					echoe('Error in %s plugin:' % p)
					import traceback
					traceback.print_exc()

		return plugins


ORGMODE = OrgMode()

# vim: set noexpandtab:
ftplugin/orgmode/plugins/Todo.py	[[[1
345
# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, apply_count, repeat, realign_tags, settings
from orgmode.liborgmode.base import Direction
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug

import vim


# temporary todo states for differnent orgmode buffers
ORGTODOSTATES = {}

def split_access_key(t):
	u"""
	:t:		todo state

	:return:	todo state and access key separated (TODO, ACCESS_KEY)
	"""
	if type(t) != unicode:
		return (None, None)

	idx = t.find(u'(')
	v, k = ((t[:idx], t[idx + 1:-1]) if t[idx + 1:-1] else (t, None)) if idx != -1 else (t, None)
	return (v, k)

class Todo(object):
	u"""
	Todo plugin.

	Description taken from orgmode.org:

	You can use TODO keywords to indicate different sequential states in the
	process of working on an item, for example:

	["TODO", "FEEDBACK", "VERIFY", "|", "DONE", "DELEGATED"]

	The vertical bar separates the TODO keywords (states that need action) from
	the DONE states (which need no further action). If you don't provide the
	separator bar, the last state is used as the DONE state. With this setup,
	the command ``,d`` will cycle an entry from TODO to FEEDBACK, then to
	VERIFY, and finally to DONE and DELEGATED.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&TODO Lists')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def _get_next_state(cls, current_state, all_states,
			direction=Direction.FORWARD, interactive=False, next_set=False):
		u"""
		:current_state:		the current todo state
		:all_states:		a list containing all todo states within sublists.
							The todo states may contain access keys
		:direction:			direction of state or keyword set change (forward/backward)
		:interactive:		if interactive and more than one todo sequence is
							specified, open a selection window
		:next_set:			advance to the next keyword set in defined direction

		:return:			return the next state as string, or NONE if the
							next state is no state.
		"""
		if not all_states:
			return

		def find_current_todo_state(c, a, stop=0):
			u"""
			:c:		current todo state
			:a:		list of todo states
			:stop:	internal parameter for parsing only two levels of lists

			:return:	first position of todo state in list in the form
						(IDX_TOPLEVEL, IDX_SECOND_LEVEL (0|1), IDX_OF_ITEM)
			"""
			for i in xrange(0, len(a)):
				if type(a[i]) in (tuple, list) and stop < 2:
					r = find_current_todo_state(c, a[i], stop=stop + 1)
					if r:
						r.insert(0, i)
						return r
				# ensure that only on the second level of sublists todo states
				# are found
				if type(a[i]) == unicode and stop == 2:
					_i = split_access_key(a[i])[0]
					if c == _i:
						return [i]

		ci = find_current_todo_state(current_state, all_states)

		if not ci:
			if next_set and direction == Direction.BACKWARD:
				echom(u'Already at the first keyword set')
				return current_state

			return split_access_key(all_states[0][0][0] if all_states[0][0] else all_states[0][1][0])[0] \
					if direction == Direction.FORWARD else \
					split_access_key(all_states[0][1][-1] if all_states[0][1] else all_states[0][0][-1])[0]
		elif next_set:
			if direction == Direction.FORWARD and ci[0] + 1 < len(all_states[ci[0]]):
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] + 1][0]), u', '.join(all_states[ci[0] + 1][1])))
				return split_access_key(all_states[ci[0] + 1][0][0] \
						if all_states[ci[0] + 1][0] else all_states[ci[0] + 1][1][0])[0]
			elif current_state is not None and direction == Direction.BACKWARD and ci[0] - 1 >= 0:
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] - 1][0]), u', '.join(all_states[ci[0] - 1][1])))
				return split_access_key(all_states[ci[0] - 1][0][0] \
						if all_states[ci[0] - 1][0] else all_states[ci[0] - 1][1][0])[0]
			else:
				echom(u'Already at the %s keyword set' % (u'first' if direction == Direction.BACKWARD else u'last'))
				return current_state
		else:
			next_pos = ci[2] + 1 if direction == Direction.FORWARD else ci[2] - 1
			if direction == Direction.FORWARD:
				if next_pos < len(all_states[ci[0]][ci[1]]):
					# select next state within done or todo states
					return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

				elif not ci[1] and next_pos - len(all_states[ci[0]][ci[1]]) < len(all_states[ci[0]][ci[1] + 1]):
					# finished todo states, jump to done states
					return split_access_key(all_states[ci[0]][ci[1] + 1][next_pos - len(all_states[ci[0]][ci[1]])])[0]
			else:
				if next_pos >= 0:
					# select previous state within done or todo states
					return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

				elif ci[1] and len(all_states[ci[0]][ci[1] - 1]) + next_pos < len(all_states[ci[0]][ci[1] - 1]):
					# finished done states, jump to todo states
					return split_access_key(all_states[ci[0]][ci[1] - 1][len(all_states[ci[0]][ci[1] - 1]) + next_pos])[0]

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def toggle_todo_state(cls, direction=Direction.FORWARD, interactive=False, next_set=False):
		u""" Toggle state of TODO item

		:returns: The changed heading
		"""
		d = ORGMODE.get_document(allow_dirty=True)

		# get heading
		heading = d.find_current_heading()
		if not heading:
			vim.eval(u'feedkeys("^", "n")')
			return

		todo_states = d.get_todo_states(strip_access_key=False)
		# get todo states
		if not todo_states:
			echom(u'No todo keywords configured.')
			return

		current_state = heading.todo

		# get new state interactively
		if interactive:
			# determine position of the interactive prompt
			prompt_pos = settings.get(u'org_todo_prompt_position', u'botright')
			if not prompt_pos in [u'botright', u'topleft']:
				prompt_pos = u'botright'

			# pass todo states to new window
			ORGTODOSTATES[d.bufnr] = todo_states
			settings.set(u'org_current_state_%d' % d.bufnr, \
					current_state if current_state is not None else u'', overwrite=True)
			todo_buffer_exists = bool(int(vim.eval((u'bufexists("org:todo/%d")'
					% (d.bufnr, )).encode(u'utf-8'))))
			if todo_buffer_exists:
				# if the buffer already exists, reuse it
				vim.command((u'%s sbuffer org:todo/%d' %
						(prompt_pos, d.bufnr, )).encode(u'utf-8'))
			else:
				# create a new window
				vim.command((u'keepalt %s %dsplit org:todo/%d' %
						(prompt_pos, len(todo_states), d.bufnr)).encode(u'utf-8'))
		else:
			new_state = Todo._get_next_state(current_state, todo_states,
					direction=direction, interactive=interactive,
					next_set=next_set)
			cls.set_todo_state(new_state)

		# plug
		plug = u'OrgTodoForward'
		if direction == Direction.BACKWARD:
			plug = u'OrgTodoBackward'

		return plug

	@classmethod
	def set_todo_state(cls, state):
		u""" Set todo state for buffer.

		:bufnr:		Number of buffer the todo state should be updated for
		:state:		The new todo state
		"""
		lineno, colno = vim.current.window.cursor
		d = ORGMODE.get_document(allow_dirty=True)
		heading = d.find_current_heading()

		if not heading:
			return

		current_state = heading.todo

		# set new headline
		heading.todo = state
		d.write_heading(heading)

		# move cursor along with the inserted state only when current position
		# is in the heading; otherwite do nothing
		if heading.start_vim == lineno and colno > heading.level:
			if current_state is not None and \
					colno <= heading.level + len(current_state):
				# the cursor is actually on the todo keyword
				# move it back to the beginning of the keyword in that case
				vim.current.window.cursor = (lineno, heading.level + 1)
			else:
				# the cursor is somewhere in the text, move it along
				if current_state is None and state is None:
					offset = 0
				elif current_state is None and state is not None:
					offset = len(state) + 1
				elif current_state is not None and state is None:
					offset = -len(current_state) - 1
				else:
					offset = len(state) - len(current_state)
				vim.current.window.cursor = (lineno, colno + offset)

	@classmethod
	def init_org_todo(cls):
		u""" Initialize org todo selection window.
		"""
		bufnr = int(vim.current.buffer.name.split('/')[-1])
		all_states = ORGTODOSTATES.get(bufnr, None)

		# because timeoutlen can only be set globally it needs to be stored and restored later
		vim.command(u'let g:org_sav_timeoutlen=&timeoutlen'.encode(u'utf-8'))
		vim.command(u'au orgmode BufEnter <buffer> :if ! exists("g:org_sav_timeoutlen")|let g:org_sav_timeoutlen=&timeoutlen|set timeoutlen=1|endif'.encode(u'utf-8'))
		vim.command(u'au orgmode BufLeave <buffer> :if exists("g:org_sav_timeoutlen")|let &timeoutlen=g:org_sav_timeoutlen|unlet g:org_sav_timeoutlen|endif'.encode(u'utf-8'))
		# make window a scratch window and set the statusline differently
		vim.command(u'setlocal tabstop=16 buftype=nofile timeout timeoutlen=1 winfixheight'.encode(u'utf-8'))
		vim.command((u'setlocal statusline=Org\\ todo\\ (%s)' % vim.eval((u'fnameescape(fnamemodify(bufname(%d), ":t"))' % bufnr).encode(u'utf-8'))).encode(u'utf-8'))
		vim.command((u'nnoremap <silent> <buffer> <Esc> :%sbw<CR>' % (vim.eval(u'bufnr("%")'.encode(u'utf-8')), )).encode(u'utf-8'))
		vim.command(u'nnoremap <silent> <buffer> <CR> :let g:org_state = fnameescape(expand("<cword>"))<Bar>bw<Bar>exec "py ORGMODE.plugins[u\'Todo\'].set_todo_state(\'".g:org_state."\')"<Bar>unlet! g:org_state<CR>'.encode(u'utf-8'))

		if all_states is None:
			vim.command(u'bw'.encode(u'utf-8'))
			echom(u'No todo states avaiable for buffer %s' % vim.current.buffer.name)

		for l in xrange(0, len(all_states)):
			res = u''
			did_done = False
			for j in xrange(0, 2):
				if j < len(all_states[l]):
					for i in all_states[l][j]:
						if type(i) != unicode:
							continue
						v, k = split_access_key(i)
						if k:
							res += (u'\t' if res else u'') + u'[%s] %s' % (k, v)
							# map access keys to callback that updates current heading
							# map selection keys
							vim.command((u'nnoremap <silent> <buffer> %s :bw<Bar>py ORGMODE.plugins[u"Todo"].set_todo_state("%s".decode(u"utf-8"))<CR>' % (k, v)).encode(u'utf-8') )
						elif v:
							res += (u'\t' if res else u'') + v
			if res:
				if l == 0:
					# WORKAROUND: the cursor can not be positioned properly on
					# the first line. Another line is just inserted and it
					# works great
					vim.current.buffer[0] = u''.encode(u'utf-8')
				vim.current.buffer.append(res.encode(u'utf-8'))

		# position the cursor of the current todo item
		vim.command(u'normal! G'.encode(u'utf-8'))
		current_state = settings.unset(u'org_current_state_%d' % bufnr)
		found = False
		if current_state is not None and current_state != '':
			for i in xrange(0, len(vim.current.buffer)):
				idx = vim.current.buffer[i].find(current_state)
				if idx != -1:
					vim.current.window.cursor = (i + 1, idx)
					found = True
					break
		if not found:
			vim.current.window.cursor = (2, 4)

		# finally make buffer non modifiable
		vim.command(u'setfiletype orgtodo'.encode(u'utf-8'))
		vim.command(u'setlocal nomodifiable'.encode(u'utf-8'))

		# remove temporary todo states for the current buffer
		del ORGTODOSTATES[bufnr]

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding(u'<localleader>ct', Plug(
			u'OrgTodoToggle',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=False)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/-', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>d', Plug(
			u'OrgTodoToggleInteractive',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=True)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/- (interactiv)', self.keybindings[-1])

		# add submenu
		submenu = self.menu + Submenu(u'Select &keyword')

		self.keybindings.append(Keybinding(u'<S-Right>', Plug(
			u'OrgTodoForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry(u'&Next keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Left>', Plug(
			u'OrgTodoBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2)<CR>')))
		submenu + ActionEntry(u'&Previous keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Right>', Plug(
			u'OrgTodoSetForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(next_set=True)<CR>')))
		submenu + ActionEntry(u'Next keyword &set', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Left>', Plug(
			u'OrgTodoSetBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2, next_set=True)<CR>')))
		submenu + ActionEntry(u'Previous &keyword set', self.keybindings[-1])

		settings.set(u'org_todo_keywords', [u'TODO'.encode(u'utf-8'), u'|'.encode(u'utf-8'), u'DONE'.encode(u'utf-8')])

		settings.set(u'org_todo_prompt_position', u'botright')

		vim.command(u'au orgmode BufReadCmd org:todo/* :py ORGMODE.plugins[u"Todo"].init_org_todo()'.encode(u'utf-8'))

# vim: set noexpandtab:
ftplugin/orgmode/plugins/Export.py	[[[1
70
# -*- coding: utf-8 -*-

from orgmode import ORGMODE
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug
from orgmode import settings

import vim


class Export(object):
	u"""
	Export a orgmode file using emacs orgmode.

	This is a *very simple* wrapper of the emacs/orgmode export.  emacs and
	orgmode need to be installed. We simply call emacs with some options to
	export the .org.

	TODO: Offer export options in vim. Don't use the menu.
	TODO: Maybe use a native implementation.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Export')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def topdf(cls):
		u"""
		Export the current buffer as pdf using emacs orgmode.
		"""
		cmd = "!emacs -nw --batch --visit=%:p --funcall=org-export-as-pdf"
		vim.command(cmd)

	@classmethod
	def tohtml(cls):
		u"""
		Export the current buffer as html using emacs orgmode.
		"""
		cmd = "!emacs -nw --batch --visit=%:p --funcall=org-export-as-html"
		vim.command(cmd)

	def register(self):
		u"""
		Registration and keybindings.
		"""

		# to PDF
		self.keybindings.append(Keybinding(u'<localleader>ep',
				Plug(u'OrgExportToPDF',
				u':py ORGMODE.plugins[u"Export"].topdf()<CR>')))
		self.menu + ActionEntry(u'To PDF (via Emacs)', self.keybindings[-1])

		# to HTML
		self.keybindings.append(Keybinding(u'<localleader>eh',
				Plug(u'OrgExportToHTML',
				u':py ORGMODE.plugins[u"Export"].tohtml()<CR>')))
		self.menu + ActionEntry(u'To HTML (via Emacs)', self.keybindings[-1])

# vim: set noexpandtab:
ftplugin/orgmode/plugins/__init__.py	[[[1
1
# -*- coding: utf-8 -*-
ftplugin/orgmode/plugins/Misc.py	[[[1
170
# -*- coding: utf-8 -*-

from orgmode import ORGMODE, apply_count
from orgmode.menu import Submenu
from orgmode.keybinding import Keybinding, Plug, MODE_VISUAL, MODE_OPERATOR

import vim

class Misc(object):
	u""" Miscellaneous functionality """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Misc')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def jump_to_first_character(cls):
		heading = ORGMODE.get_document().current_heading()
		if not heading:
			vim.eval(u'feedkeys("^", "n")'.encode(u'utf-8'))
			return

		vim.current.window.cursor = (vim.current.window.cursor[0], heading.level + 1)

	@classmethod
	def edit_at_first_character(cls):
		heading = ORGMODE.get_document().current_heading()
		if not heading or heading.start_vim != vim.current.window.cursor[0]:
			vim.eval(u'feedkeys("I", "n")'.encode(u'utf-8'))
			return

		vim.current.window.cursor = (vim.current.window.cursor[0], heading.level + 1)
		vim.command(u'startinsert'.encode(u'utf-8'))

	#@repeat
	@classmethod
	@apply_count
	def i_heading(cls, mode=u'visual', selection=u'inner', skip_children=False):
		u"""
		inner heading text object
		"""
		heading = ORGMODE.get_document().current_heading()
		if heading:
			if selection != u'inner':
				heading = heading if not heading.parent else heading.parent

			line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
			line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]

			if mode != u'visual':
				line_start = vim.current.window.cursor[0]
				line_end = line_start

			start = line_start
			end = line_end
			move_one_character_back = u'' if mode == u'visual' else u'h'

			if heading.start_vim < line_start:
				start = heading.start_vim
			if heading.end_vim > line_end and not skip_children:
				end = heading.end_vim
			elif heading.end_of_last_child_vim > line_end and skip_children:
				end = heading.end_of_last_child_vim

			if mode != u'visual' and not vim.current.buffer[end - 1]:
				end -= 1
				move_one_character_back = u''

			swap_cursor = u'o' if vim.current.window.cursor[0] == line_start else u''

			if selection == u'inner' and vim.current.window.cursor[0] != line_start:
				h = ORGMODE.get_document().current_heading()
				if h:
					heading = h

			visualmode = vim.eval(u'visualmode()').decode(u'utf-8') if mode == u'visual' else u'v'

			if line_start == start and line_start != heading.start_vim:
				if col_start in (0, 1):
					vim.command((u'normal! %dgg0%s%dgg$%s%s' % \
							(start, visualmode, end, move_one_character_back, swap_cursor)).encode(u'utf-8'))
				else:
					vim.command((u'normal! %dgg0%dl%s%dgg$%s%s' % \
							(start, col_start - 1, visualmode, end, move_one_character_back, swap_cursor)).encode(u'utf-8'))
			else:
				vim.command((u'normal! %dgg0%dl%s%dgg$%s%s' % \
						(start, heading.level + 1, visualmode, end, move_one_character_back, swap_cursor)).encode(u'utf-8'))

			if selection == u'inner':
				if mode == u'visual':
					return u'OrgInnerHeadingVisual' if not skip_children else u'OrgInnerTreeVisual'
				else:
					return u'OrgInnerHeadingOperator' if not skip_children else u'OrgInnerTreeOperator'
			else:
				if mode == u'visual':
					return u'OrgOuterHeadingVisual' if not skip_children else u'OrgOuterTreeVisual'
				else:
					return u'OrgOuterHeadingOperator' if not skip_children else u'OrgOuterTreeOperator'
		elif mode == u'visual':
			vim.command(u'normal! gv'.encode(u'utf-8'))

	#@repeat
	@classmethod
	@apply_count
	def a_heading(cls, selection=u'inner', skip_children=False):
		u"""
		a heading text object
		"""
		heading = ORGMODE.get_document().current_heading()
		if heading:
			if selection != u'inner':
				heading = heading if not heading.parent else heading.parent

			line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
			line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]

			start = line_start
			end = line_end

			if heading.start_vim < line_start:
				start = heading.start_vim
			if heading.end_vim > line_end and not skip_children:
				end = heading.end_vim
			elif heading.end_of_last_child_vim > line_end and skip_children:
				end = heading.end_of_last_child_vim

			swap_cursor = u'o' if vim.current.window.cursor[0] == line_start else u''

			vim.command((u'normal! %dgg%s%dgg$%s' % \
					(start, vim.eval(u'visualmode()'.encode(u'utf-8')), end, swap_cursor)).encode(u'utf-8'))
			if selection == u'inner':
				return u'OrgAInnerHeadingVisual' if not skip_children else u'OrgAInnerTreeVisual'
			else:
				return u'OrgAOuterHeadingVisual' if not skip_children else u'OrgAOuterTreeVisual'
		else:
			vim.command(u'normal! gv'.encode(u'utf-8'))

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding(u'^', Plug(u'OrgJumpToFirstCharacter', u':py ORGMODE.plugins[u"Misc"].jump_to_first_character()<CR>')))
		self.keybindings.append(Keybinding(u'I', Plug(u'OrgEditAtFirstCharacter', u':py ORGMODE.plugins[u"Misc"].edit_at_first_character()<CR>')))

		self.keybindings.append(Keybinding(u'ih', Plug(u'OrgInnerHeadingVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading()<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'ah', Plug(u'OrgAInnerHeadingVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].a_heading()<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'Oh', Plug(u'OrgOuterHeadingVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(selection=u"outer")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'OH', Plug(u'OrgAOuterHeadingVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].a_heading(selection=u"outer")<CR>', mode=MODE_VISUAL)))

		self.keybindings.append(Keybinding(u'ih', Plug(u'OrgInnerHeadingOperator', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'ah', u':normal Vah<CR>', mode=MODE_OPERATOR))
		self.keybindings.append(Keybinding(u'Oh', Plug(u'OrgOuterHeadingOperator', ':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(mode=u"operator", selection=u"outer")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'OH', u':normal VOH<CR>', mode=MODE_OPERATOR))

		self.keybindings.append(Keybinding(u'ir', Plug(u'OrgInnerTreeVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'ar', Plug(u'OrgAInnerTreeVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].a_heading(skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'Or', Plug(u'OrgOuterTreeVisual', u'<:<C-u>py ORGMODE.plugins[u"Misc"].i_heading(selection=u"outer", skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'OR', Plug(u'OrgAOuterTreeVisual', u':<C-u>py ORGMODE.plugins[u"Misc"].a_heading(selection=u"outer", skip_children=True)<CR>', mode=MODE_VISUAL)))

		self.keybindings.append(Keybinding(u'ir', Plug(u'OrgInnerTreeOperator', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'ar', u':normal Var<CR>', mode=MODE_OPERATOR))
		self.keybindings.append(Keybinding(u'Or', Plug(u'OrgOuterTreeOperator', u':<C-u>py ORGMODE.plugins[u"Misc"].i_heading(mode=u"operator", selection=u"outer", skip_children=True)<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'OR', u':normal VOR<CR>', mode=MODE_OPERATOR))
ftplugin/orgmode/plugins/Hyperlinks.py	[[[1
169
# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, realign_tags
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command

import vim
import re

class Hyperlinks(object):
	u""" Hyperlinks plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Hyperlinks')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	uri_match = re.compile(r'^\[{2}(?P<uri>[^][]*)(\]\[(?P<description>[^][]*))?\]{2}')

	@classmethod
	def _get_link(cls, cursor=None):
		u"""
		Get the link the cursor is on and return it's URI and description

		:cursor: None or (Line, Column)
		:returns: None if no link was found, otherwise {uri:URI, description:DESCRIPTION, line:LINE, start:START, end:END} or uri and description could be None if not set
		"""
		cursor = cursor if cursor else vim.current.window.cursor
		line = vim.current.buffer[cursor[0] - 1].decode(u'utf-8')

		# if the cursor is on the last bracket, it's not recognized as a hyperlink
		start = line.rfind(u'[[', 0, cursor[1])
		if start == -1:
			start = line.rfind(u'[[', 0, cursor[1] + 2)
		end = line.find(u']]', cursor[1])
		if end == -1:
			end = line.find(u']]', cursor[1] - 1)

		# extract link
		if start != -1 and end != -1:
			end += 2
			match = Hyperlinks.uri_match.match(line[start:end])

			res = {u'line':line, u'start':start, u'end':end, u'uri':None, u'description':None}
			if match:
				res.update(match.groupdict())
			return res

	@classmethod
	def follow(cls, action=u'openLink', visual=u''):
		u""" Follow hyperlink. If called on a regular string UTL determines the
		outcome. Normally a file with that name will be opened.

		:action: "copy" if the link should be copied to clipboard, otherwise the link will be opened
		:visual: "visual" if Universal Text Linking should be triggered in visual mode

		:returns: URI or None
		"""
		if not int(vim.eval(u'exists(":Utl")')):
			echom(u'Universal Text Linking plugin not installed, unable to proceed.')
			return

		action = u'copyLink' if action and action.startswith(u'copy') else u'openLink'
		visual = u'visual' if visual and visual.startswith(u'visual') else u''

		link = Hyperlinks._get_link()

		if link and link[u'uri'] is not None:
			# call UTL with the URI
			vim.command((u'Utl %s %s %s' % (action, visual, link[u'uri'])).encode(u'utf-8'))
			return link[u'uri']
		else:
			# call UTL and let it decide what to do
			vim.command((u'Utl %s %s' % (action, visual)).encode(u'utf-8'))

	@classmethod
	@realign_tags
	def insert(cls, uri=None, description=None):
		u""" Inserts a hyperlink. If no arguments are provided, an interactive
		query will be started.

		:uri: The URI that will be opened
		:description: An optional description that will be displayed instead of the URI

		:returns: (URI, description)
		"""
		link = Hyperlinks._get_link()
		if link:
			if uri is None and link[u'uri'] is not None:
				uri = link[u'uri']
			if description is None and link[u'description'] is not None:
				description = link[u'description']

		if uri is None:
			uri = vim.eval(u'input("Link: ", "", "file")')
		elif link:
			uri = vim.eval(u'input("Link: ", "%s", "file")' % link[u'uri'])
		if uri is None:
			return
		else:
			uri = uri.decode(u'utf-8')

		if description is None:
			description = vim.eval(u'input("Description: ")').decode(u'utf-8')
		elif link:
			description = vim.eval(u'input("Description: ", "%s")' % link[u'description']).decode(u'utf-8')
		if description is None:
			return

		cursor = vim.current.window.cursor
		cl = vim.current.buffer[cursor[0] - 1].decode(u'utf-8')
		head = cl[:cursor[1] + 1] if not link else cl[:link[u'start']]
		tail = cl[cursor[1] + 1:] if not link else cl[link[u'end']:]

		separator = u''
		if description:
			separator = u']['

		if uri or description:
			vim.current.buffer[cursor[0] - 1] = (u''.join((head, u'[[%s%s%s]]' % (uri, separator, description), tail))).encode(u'utf-8')
		elif link:
			vim.current.buffer[cursor[0] - 1] = (u''.join((head, tail))).encode(u'utf-8')

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.commands.append(Command(u'OrgHyperlinkFollow', u':py ORGMODE.plugins[u"Hyperlinks"].follow()'))
		self.keybindings.append(Keybinding(u'gl', Plug(u'OrgHyperlinkFollow', self.commands[-1])))
		self.menu + ActionEntry(u'&Follow Link', self.keybindings[-1])

		self.commands.append(Command(u'OrgHyperlinkCopy', u':py ORGMODE.plugins[u"Hyperlinks"].follow(action=u"copy")'))
		self.keybindings.append(Keybinding(u'gyl', Plug(u'OrgHyperlinkCopy', self.commands[-1])))
		self.menu + ActionEntry(u'&Copy Link', self.keybindings[-1])

		self.commands.append(Command(u'OrgHyperlinkInsert', u':py ORGMODE.plugins[u"Hyperlinks"].insert(<f-args>)', arguments=u'*'))
		self.keybindings.append(Keybinding(u'gil', Plug(u'OrgHyperlinkInsert', self.commands[-1])))
		self.menu + ActionEntry(u'&Insert Link', self.keybindings[-1])

		self.menu + Separator()

		# find next link
		self.commands.append(Command(u'OrgHyperlinkNextLink', u":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 's') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding(u'gn', Plug(u'OrgHyperlinkNextLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Next Link', self.keybindings[-1])

		# find previous link
		self.commands.append(Command(u'OrgHyperlinkPreviousLink', u":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 'bs') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding(u'go', Plug(u'OrgHyperlinkPreviousLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Previous Link', self.keybindings[-1])

		self.menu + Separator()

		# Descriptive Links
		self.commands.append(Command(u'OrgHyperlinkDescriptiveLinks', u':setlocal cole=2'))
		self.menu + ActionEntry(u'&Descriptive Links', self.commands[-1])

		# Literal Links
		self.commands.append(Command(u'OrgHyperlinkLiteralLinks', u':setlocal cole=0'))
		self.menu + ActionEntry(u'&Literal Links', self.commands[-1])
ftplugin/orgmode/plugins/TagsProperties.py	[[[1
155
# -*- coding: utf-8 -*-

from orgmode import ORGMODE, repeat
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode import settings

import vim

class TagsProperties(object):
	u""" TagsProperties plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&TAGS and Properties')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def complete_tags(cls):
		u""" build a list of tags and store it in variable b:org_tag_completion
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			return

		leading_portion = vim.eval(u'a:ArgLead').decode(u'utf-8')
		cursor = int(vim.eval(u'a:CursorPos'))

		# extract currently completed tag
		idx_orig = leading_portion.rfind(u':', 0, cursor)
		if idx_orig == -1:
			idx = 0
		else:
			idx = idx_orig

		current_tag = leading_portion[idx: cursor].lstrip(u':')
		head = leading_portion[:idx + 1]
		if idx_orig == -1:
			head = u''
		tail = leading_portion[cursor:]

		# extract all tags of the current file
		all_tags = set()
		for h in d.all_headings():
			for t in h.tags:
				all_tags.add(t)

		ignorecase = bool(int(settings.get(u'org_tag_completion_ignorecase', int(vim.eval(u'&ignorecase')))))
		possible_tags = []
		current_tags = heading.tags
		for t in all_tags:
			if ignorecase:
				if t.lower().startswith(current_tag.lower()):
					possible_tags.append(t)
			elif t.startswith(current_tag):
				possible_tags.append(t)

		vim.command((u'let b:org_complete_tags = [%s]' % u', '.join([u'"%s%s:%s"' % (head, i, tail) for i in possible_tags])).encode(u'utf-8'))

	@classmethod
	@repeat
	def set_tags(cls):
		u""" Set tags for current heading
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			return

		# retrieve tags
		res = None
		if heading.tags:
			res = vim.eval(u'input("Tags: ", ":%s:", "customlist,Org_complete_tags")' % u':'.join(heading.tags))
		else:
			res = vim.eval(u'input("Tags: ", "", "customlist,Org_complete_tags")')

		if res is None:
			# user pressed <Esc> abort any further processing
			return

		# remove empty tags
		heading.tags = filter(lambda x: x.strip() != u'', res.decode(u'utf-8').strip().strip(u':').split(u':'))

		d.write()

		return u'OrgSetTags'

	@classmethod
	def realign_tags(cls):
		u"""
		Updates tags when user finished editing a heading
		"""
		d = ORGMODE.get_document(allow_dirty=True)
		heading = d.find_current_heading()
		if not heading:
			return

		if vim.current.window.cursor[0] == heading.start_vim:
			heading.set_dirty_heading()
			d.write_heading(heading, including_children=False)

	@classmethod
	def realign_all_tags(cls):
		u"""
		Updates tags when user finishes editing a heading
		"""
		d = ORGMODE.get_document()
		for heading in d.all_headings():
			heading.set_dirty_heading()

		d.write()

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		settings.set(u'org_tag_column', u'77')

		settings.set(u'org_tag_completion_ignorecase', int(vim.eval(u'&ignorecase')))

		self.keybindings.append(Keybinding(u'<localleader>st', Plug(u'OrgSetTags', u':py ORGMODE.plugins[u"TagsProperties"].set_tags()<CR>')))
		self.menu + ActionEntry(u'Set &Tags', self.keybindings[-1])

		self.commands.append(Command(u'OrgTagsRealign', u":py ORGMODE.plugins[u'TagsProperties'].realign_all_tags()"))

		# workaround to align tags when user is leaving insert mode
		vim.command(u"""function Org_complete_tags(ArgLead, CmdLine, CursorPos)
python << EOF
ORGMODE.plugins[u'TagsProperties'].complete_tags()
EOF
if exists('b:org_complete_tags')
	let tmp = b:org_complete_tags
	unlet b:org_complete_tags
	return tmp
else
	return []
endif
endfunction""".encode(u'utf-8'))

		# this is for all org files opened after this file
		vim.command(u"au orgmode FileType org :au orgmode InsertLeave <buffer> :py ORGMODE.plugins[u'TagsProperties'].realign_tags()".encode(u'utf-8'))

		# this is for the current file
		vim.command(u"au orgmode InsertLeave <buffer> :py ORGMODE.plugins[u'TagsProperties'].realign_tags()".encode(u'utf-8'))
ftplugin/orgmode/plugins/Date.py	[[[1
260
# -*- coding: utf-8 -*-
import re
from datetime import timedelta, date, datetime

import vim
from orgmode import ORGMODE, settings, echom, insert_at_cursor, get_user_input
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry


class Date(object):
	u"""
	Handles all date and timestamp related tasks.

	TODO: extend functionality (calendar, repetitions, ranges). See
			http://orgmode.org/guide/Dates-and-Times.html#Dates-and-Times
	"""

	date_regex = r"\d\d\d\d-\d\d-\d\d"
	datetime_regex = r"[A-Z]\w\w \d\d\d\d-\d\d-\d\d \d\d:\d\d>"

	month_mapping = {u'jan': 1, u'feb': 2, u'mar': 3, u'apr': 4, u'may': 5,
			u'jun': 6, u'jul': 7, u'aug': 8, u'sep': 9, u'oct': 10, u'nov': 11,
			u'dec': 12}

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Dates and Scheduling')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

		# set speeddating format that is compatible with orgmode
		try:
			if int(vim.eval(u'exists(":SpeedDatingFormat")'.encode(u'utf-8'))):
				vim.command(u':1SpeedDatingFormat %Y-%m-%d %a'.encode(u'utf-8'))
				vim.command(u':1SpeedDatingFormat %Y-%m-%d %a %H:%M'.encode(u'utf-8'))
			else:
				echom(u'Speeddating plugin not installed. Please install it.')
		except:
			echom(u'Speeddating plugin not installed. Please install it.')

	@classmethod
	def _modify_time(cls, startdate, modifier):
		u"""Modify the given startdate according to modifier. Return the new
		date or datetime.

		See http://orgmode.org/manual/The-date_002ftime-prompt.html
		"""
		if modifier is None or modifier == '' or modifier == '.':
			return startdate

		# rm crap from modifier
		modifier = modifier.strip()

		# check real date
		date_regex = r"(\d\d\d\d)-(\d\d)-(\d\d)"
		match = re.search(date_regex, modifier)
		if match:
			year, month, day = match.groups()
			newdate = date(int(year), int(month), int(day))

		# check abbreviated date, seperated with '-'
		date_regex = u"(\d{1,2})-(\d+)-(\d+)"
		match = re.search(date_regex, modifier)
		if match:
			year, month, day = match.groups()
			newdate = date(2000 + int(year), int(month), int(day))

		# check abbreviated date, seperated with '/'
		# month/day
		date_regex = u"(\d{1,2})/(\d{1,2})"
		match = re.search(date_regex, modifier)
		if match:
			month, day = match.groups()
			newdate = date(startdate.year, int(month), int(day))
			# date should be always in the future
			if newdate < startdate:
				newdate = date(startdate.year + 1, int(month), int(day))

		# check full date, seperated with 'space'
		# month day year
		# 'sep 12 9' --> 2009 9 12
		date_regex = u"(\w\w\w) (\d{1,2}) (\d{1,2})"
		match = re.search(date_regex, modifier)
		if match:
			gr = match.groups()
			day = int(gr[1])
			month = int(cls.month_mapping[gr[0]])
			year = 2000 + int(gr[2])
			newdate = date(year, int(month), int(day))

		# check days as integers
		date_regex = u"^(\d{1,2})$"
		match = re.search(date_regex, modifier)
		if match:
			newday, = match.groups()
			newday = int(newday)
			if newday > startdate.day:
				newdate = date(startdate.year, startdate.month, newday)
			else:
				# TODO: DIRTY, fix this
				#       this does NOT cover all edge cases
				newdate = startdate + timedelta(days=28)
				newdate = date(newdate.year, newdate.month, newday)

		# check for full days: Mon, Tue, Wed, Thu, Fri, Sat, Sun
		modifier_lc = modifier.lower()
		match = re.search(u'mon|tue|wed|thu|fri|sat|sun', modifier_lc)
		if match:
			weekday_mapping = {u'mon': 0, u'tue': 1, u'wed': 2, u'thu': 3,
					u'fri': 4, u'sat': 5, u'sun': 6}
			diff = (weekday_mapping[modifier_lc] - startdate.weekday()) % 7
			# use next weeks weekday if current weekday is the same as modifier
			if diff == 0:
				diff = 7
			newdate = startdate + timedelta(days=diff)

		# check for days modifier with appended d
		match = re.search(u'\+(\d*)d', modifier)
		if match:
			days = int(match.groups()[0])
			newdate = startdate + timedelta(days=days)

		# check for days modifier without appended d
		match = re.search(u'\+(\d*) |\+(\d*)$', modifier)
		if match:
			try:
				days = int(match.groups()[0])
			except:
				days = int(match.groups()[1])
			newdate = startdate + timedelta(days=days)

		# check for week modifier
		match = re.search(u'\+(\d+)w', modifier)
		if match:
			weeks = int(match.groups()[0])
			newdate = startdate + timedelta(weeks=weeks)

		# check for week modifier
		match = re.search(u'\+(\d+)m', modifier)
		if match:
			months = int(match.groups()[0])
			newdate = date(startdate.year, startdate.month + months, startdate.day)

		# check for year modifier
		match = re.search(u'\+(\d*)y', modifier)
		if match:
			years = int(match.groups()[0])
			newdate = date(startdate.year + years, startdate.month, startdate.day)

		# check for month day
		match = re.search(
				u'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) (\d{1,2})',
				modifier.lower())
		if match:
			month = cls.month_mapping[match.groups()[0]]
			day = int(match.groups()[1])
			newdate = date(startdate.year, int(month), int(day))
			# date should be always in the future
			if newdate < startdate:
				newdate = date(startdate.year + 1, int(month), int(day))

		# check abbreviated date, seperated with '/'
		# month/day/year
		date_regex = u"(\d{1,2})/(\d+)/(\d+)"
		match = re.search(date_regex, modifier)
		if match:
			month, day, year = match.groups()
			newdate = date(2000 + int(year), int(month), int(day))

		# check for month day year
		# sep 12 2011
		match = re.search(
				u'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) (\d{1,2}) (\d{1,4})',
				modifier.lower())
		if match:
			month = int(cls.month_mapping[match.groups()[0]])
			day = int(match.groups()[1])
			if len(match.groups()[2]) < 4:
				year = 2000 + int(match.groups()[2])
			else:
				year = int(match.groups()[2])
			newdate = date(year, month, day)

		# check for time: HH:MM
		# '12:45' --> datetime(2006, 06, 13, 12, 45))
		match = re.search(u'(\d{1,2}):(\d\d)$', modifier)
		if match:
			try:
				startdate = newdate
			except:
				pass
			return datetime(startdate.year, startdate.month, startdate.day,
					int(match.groups()[0]), int(match.groups()[1]))

		try:
			return newdate
		except:
			return startdate

	@classmethod
	def insert_timestamp(cls, active=True):
		u"""
		Insert a timestamp at the cursor position.

		TODO: show fancy calendar to pick the date from.
		TODO: add all modifier of orgmode.
		"""
		today = date.today()
		msg = u''.join([u'Inserting ',
				today.strftime(u'%Y-%m-%d %a'.encode(u'utf-8')),
				u' | Modify date'])
		modifier = get_user_input(msg)

		# abort if the user canceled the input promt
		if modifier is None:
			return

		newdate = cls._modify_time(today, modifier)

		# format
		if isinstance(newdate, datetime):
			newdate = newdate.strftime(
					u'%Y-%m-%d %a %H:%M'.encode(u'utf-8')).decode(u'utf-8')
		else:
			newdate = newdate.strftime(
					u'%Y-%m-%d %a'.encode(u'utf-8')).decode(u'utf-8')
		timestamp = u'<%s>' % newdate if active else u'[%s]' % newdate

		insert_at_cursor(timestamp)

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		self.keybindings.append(Keybinding(u'<localleader>sa',
				Plug(u'OrgDateInsertTimestampActive',
				u':py ORGMODE.plugins[u"Date"].insert_timestamp()<CR>')))
		self.menu + ActionEntry(u'Timest&amp', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>si',
				Plug(u'OrgDateInsertTimestampInactive',
					u':py ORGMODE.plugins[u"Date"].insert_timestamp(False)<CR>')))
		self.menu + ActionEntry(u'Timestamp (&inactive)', self.keybindings[-1])

		submenu = self.menu + Submenu(u'Change &Date')
		submenu + ActionEntry(u'Day &Earlier', u'<C-x>', u'<C-x>')
		submenu + ActionEntry(u'Day &Later', u'<C-a>', u'<C-a>')

# vim: set noexpandtab:
ftplugin/orgmode/plugins/LoggingWork.py	[[[1
40
# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command

import vim

class LoggingWork(object):
	u""" LoggingWork plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&Logging work')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def action(cls):
		u""" Some kind of action

		:returns: TODO
		"""
		pass

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		self.commands.append(Command(u'OrgLoggingRecordDoneTime', u':py ORGMODE.plugins[u"LoggingWork"].action()'))
		self.menu + ActionEntry(u'&Record DONE time', self.commands[-1])
ftplugin/orgmode/plugins/Agenda.py	[[[1
255
# -*- coding: utf-8 -*-

from datetime import date
import os

from orgmode import ORGMODE, settings
from orgmode import get_bufnumber
from orgmode import get_bufname
from orgmode import echoe
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry
import vim


class Agenda(object):
	u"""
	The Agenda Plugin uses liborgmode.agenda to display the agenda views.

	The main task is to format the agenda from liborgmode.agenda.
	Also all the mappings: jump from agenda to todo, etc are realized here.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Agenda')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def _switch_to(cls, bufname, vim_commands=None):
		u"""
		Swicht to the buffer with bufname.

		A list of vim.commands (if given) gets executed as well.

		TODO: this should be extracted and imporved to create an easy to use
		way to create buffers/jump to buffers. Otherwise there are going to be
		quite a few ways to open buffers in vimorgmode.
		"""
		cmds = [u'botright split org:%s' % bufname,
				u'setlocal buftype=nofile',
				u'setlocal modifiable',
				u'setlocal nonumber',
				# call opendoc() on enter the original todo item
				u'nnoremap <silent> <buffer> <CR> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc()"<CR>',
				u'nnoremap <silent> <buffer> <TAB> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc(switch=True)"<CR>',
				u'nnoremap <silent> <buffer> <S-CR> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc(split=True)"<CR>',
				# statusline
				u'setlocal statusline=Org\\ %s' % bufname
				]
		if vim_commands:
			cmds.extend(vim_commands)
		for cmd in cmds:
			vim.command(cmd.encode(u'utf-8'))

	@classmethod
	def _get_agendadocuments(self):
		u"""
		Return the org documents of the agenda files; return None if no
		agenda documents are defined.

		TODO: maybe turn this into an decorator?
		"""
		# load org files of agenda
		agenda_files = settings.get(u'org_agenda_files', u',')
		if not agenda_files or agenda_files == ',':
			echoe((u"No org_agenda_files defined. Use :let "
				u"g:org_agenda_files=['~/org/index.org'] to add " 
				u"files to the agenda view."))
			return

		agenda_files = [os.path.expanduser(f) for f in agenda_files]

		for agenda_file in agenda_files: 
			vim.command((u'badd %s' % agenda_file).encode(u'utf-8'))

		# determine the buffer nr of the agenda files
		agenda_nums = [get_bufnumber(fn) for fn in agenda_files]

		# collect all documents of the agenda files and create the agenda
		return [ORGMODE.get_document(i) for i in agenda_nums if i is not None]

	@classmethod
	def opendoc(cls, split=False, switch=False):
		u"""
		If you are in the agenda view jump to the document the item in the
		current line belongs to. cls.line2doc is used for that.

		:split: if True, open the document in a new split window.
		:switch: if True, switch to another window and open the the document
			there.
		"""
		row, _ = vim.current.window.cursor
		try:
			bufname, bufnr, destrow = cls.line2doc[row]
		except:
			return

		# reload source file if it is not loaded
		if get_bufname(bufnr) is None:
			vim.command((u'badd %s' % bufname).encode(u'utf-8'))
			bufnr = get_bufnumber(bufname)
			tmp = cls.line2doc[row]
			cls.line2doc[bufnr] = tmp
			# delete old endry
			del cls.line2doc[row]

		if split:
			vim.command((u"sbuffer %s" % bufnr).encode(u'utf-8'))
		elif switch:
			vim.command(u"wincmd w".encode(u'utf-8'))
			vim.command((u"buffer %d" % bufnr).encode(u'utf-8'))
		else:
			vim.command((u"buffer %s" % bufnr).encode(u'utf-8'))
		vim.command((u"normal! %dgg <CR>" % (destrow + 1)).encode(u'utf-8'))

	@classmethod
	def list_next_week(cls):
		agenda_documents = cls._get_agendadocuments()
		if not agenda_documents:
			return
		raw_agenda = ORGMODE.agenda_manager.get_next_week_and_active_todo(
				agenda_documents)

		# create buffer at bottom
		cmd = [u'setlocal filetype=orgagenda',
				]
		cls._switch_to(u'AGENDA', cmd)

		# line2doc is a dic with the mapping:
		#     line in agenda buffer --> source document
		# It's easy to jump to the right document this way
		cls.line2doc = {}
		# format text for agenda
		last_date = raw_agenda[0].active_date
		final_agenda = [u'Week Agenda:', unicode(last_date)]
		for i, h in enumerate(raw_agenda):
			# insert date information for every new date (not datetime)
			if unicode(h.active_date)[1:11] != unicode(last_date)[1:11]:
				today = date.today()
				# insert additional "TODAY" string
				if h.active_date.year == today.year and \
						h.active_date.month == today.month and \
						h.active_date.day == today.day:
					section = unicode(h.active_date) + u" TODAY"
					today_row = len(final_agenda) + 1
				else:
					section = unicode(h.active_date)
				final_agenda.append(section)

				# update last_date
				last_date = h.active_date

			bufname = os.path.basename(vim.buffers[h.document.bufnr-1].name)
			bufname = bufname[:-4] if bufname.endswith(u'.org') else bufname
			formated = u"  %(bufname)s (%(bufnr)d)  %(todo)s  %(title)s" % {
					'bufname': bufname,
					'bufnr':   h.document.bufnr,
					'todo':    h.todo,
					'title':   h.title
			}
			final_agenda.append(formated)
			cls.line2doc[len(final_agenda)] = (get_bufname(h.document.bufnr), h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in final_agenda ]
		vim.command(u'setlocal nomodifiable  conceallevel=2 concealcursor=nc'.encode(u'utf-8'))
		# try to jump to the positon of today
		try:
			vim.command((u'normal! %sgg<CR>' % today_row).encode(u'utf-8'))
		except:
			pass

	@classmethod
	def list_all_todos(cls):
		u"""
		List all todos in all agenda files in one buffer.
		"""
		agenda_documents = cls._get_agendadocuments()
		if not agenda_documents:
			return
		raw_agenda = ORGMODE.agenda_manager.get_todo(agenda_documents)

		cls.line2doc = {}
		# create buffer at bottom
		cmd = [u'setlocal filetype=orgagenda']
		cls._switch_to(u'AGENDA', cmd)

		# format text of agenda
		final_agenda = []
		for i, h in enumerate(raw_agenda):
			tmp = u"%s %s" % (h.todo, h.title)
			final_agenda.append(tmp)
			cls.line2doc[len(final_agenda)] = (get_bufname(h.document.bufnr), h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in final_agenda ]
		vim.command(u'setlocal nomodifiable  conceallevel=2 concealcursor=nc'.encode(u'utf-8'))

	@classmethod
	def list_timeline(cls):
		"""
		List a timeline of the current buffer to get an overview of the
		current file.
		"""
		raw_agenda = ORGMODE.agenda_manager.get_timestamped_items(
				[ORGMODE.get_document()])

		# create buffer at bottom
		cmd = [u'setlocal filetype=orgagenda']
		cls._switch_to(u'AGENDA', cmd)

		cls.line2doc = {}
		# format text of agenda
		final_agenda = []
		for i, h in enumerate(raw_agenda):
			tmp = u"%s %s" % (h.todo, h.title)
			final_agenda.append(tmp)
			cls.line2doc[len(final_agenda)] = (get_bufname(h.document.bufnr), h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in final_agenda ]
		vim.command(u'setlocal nomodifiable conceallevel=2 concealcursor=nc'.encode(u'utf-8'))

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		self.keybindings.append(Keybinding(u'<localleader>cat',
				Plug(u'OrgAgendaTodo',
				u':py ORGMODE.plugins[u"Agenda"].list_all_todos()<CR>')))
		self.menu + ActionEntry(u'Agenda for all TODOs', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>caa',
				Plug(u'OrgAgendaWeek',
				u':py ORGMODE.plugins[u"Agenda"].list_next_week()<CR>')))
		self.menu + ActionEntry(u'Agenda for the week', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>caL',
				Plug(u'OrgAgendaTimeline',
				u':py ORGMODE.plugins[u"Agenda"].list_timeline()<CR>')))
		self.menu + ActionEntry(u'Timeline for this buffer',
				self.keybindings[-1])

# vim: set noexpandtab:
ftplugin/orgmode/plugins/Navigator.py	[[[1
313
# -*- coding: utf-8 -*-

from orgmode import echo, ORGMODE, apply_count
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, MODE_VISUAL, MODE_OPERATOR, Plug
from orgmode.liborgmode.documents import Direction

import vim

class Navigator(object):
	u""" Implement navigation in org-mode documents """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + Submenu(u'&Navigate Headings')
		self.keybindings = []

	@classmethod
	@apply_count
	def parent(cls, mode):
		u"""
		Focus parent heading

		:returns: parent heading or None
		"""
		heading = ORGMODE.get_document().current_heading()
		if not heading:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No heading found')
			return

		if not heading.parent:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No parent heading found')
			return

		p = heading.parent

		if mode == u'visual':
			cls._change_visual_selection(heading, p, direction=Direction.BACKWARD, parent=True)
		else:
			vim.current.window.cursor = (p.start_vim, p.level + 1)
		return p

	@classmethod
	@apply_count
	def parent_next_sibling(cls, mode):
		u"""
		Focus the parent's next sibling

		:returns: parent's next sibling heading or None
		"""
		heading = ORGMODE.get_document().current_heading()
		if not heading:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No heading found')
			return

		if not heading.parent or not heading.parent.next_sibling:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No parent heading found')
			return

		ns = heading.parent.next_sibling

		if mode == u'visual':
			cls._change_visual_selection(heading, ns, direction=Direction.FORWARD, parent=False)
		elif mode == u'operator':
			vim.current.window.cursor = (ns.start_vim, 0)
		else:
			vim.current.window.cursor = (ns.start_vim, ns.level + 1)
		return ns

	@classmethod
	def _change_visual_selection(cls, current_heading, heading, direction=Direction.FORWARD, noheadingfound=False, parent=False):
		current = vim.current.window.cursor[0]
		line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
		line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]

		f_start = heading.start_vim
		f_end = heading.end_vim
		swap_cursor = True

		# << |visual start
		# selection end >>
		if current == line_start:
			if (direction == Direction.FORWARD and line_end < f_start) or noheadingfound and not direction == Direction.BACKWARD:
				swap_cursor = False

			# focus heading HERE
			# << |visual start
			# selection end >>

			# << |visual start
			# focus heading HERE
			# selection end >>
			if f_start < line_start and direction == Direction.BACKWARD:
				if current_heading.start_vim < line_start and not parent:
					line_start = current_heading.start_vim
				else:
					line_start = f_start

			elif (f_start < line_start or f_start < line_end) and not noheadingfound:
				line_start = f_start

			# << |visual start
			# selection end >>
			# focus heading HERE
			else:
				if direction == Direction.FORWARD:
					if line_end < f_start and not line_start == f_start - 1 and current_heading:
						# focus end of previous heading instead of beginning of next heading
						line_start = line_end
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_start = line_end
						line_end = f_end
				elif direction == Direction.BACKWARD:
					if line_end < f_end:
						pass
				else:
					line_start = line_end
					line_end = f_end

		# << visual start
		# selection end| >>
		else:
			# focus heading HERE
			# << visual start
			# selection end| >>
			if line_start > f_start and line_end > f_end and not parent:
				line_end = f_end
				swap_cursor = False

			elif (line_start > f_start or \
					line_start == f_start) and line_end <= f_end and direction == Direction.BACKWARD:
				line_end = line_start
				line_start = f_start

			# << visual start
			# selection end and focus heading end HERE| >>

			# << visual start
			# focus heading HERE
			# selection end| >>

			# << visual start
			# selection end| >>
			# focus heading HERE
			else:
				if direction == Direction.FORWARD:
					if line_end < f_start - 1:
						# focus end of previous heading instead of beginning of next heading
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_end = f_end
				else:
					line_end = f_end
				swap_cursor = False

		move_col_start = u'%dl' % (col_start - 1) if (col_start - 1) > 0 and (col_start - 1) < 2000000000 else u''
		move_col_end = u'%dl' % (col_end - 1) if (col_end - 1) > 0 and (col_end - 1) < 2000000000 else u''
		swap = u'o' if swap_cursor else u''

		vim.command((u'normal! %dgg%s%s%dgg%s%s' % \
				(line_start, move_col_start, vim.eval(u'visualmode()'.encode(u'utf-8')), line_end, move_col_end, swap)).encode(u'utf-8'))

	@classmethod
	def _focus_heading(cls, mode, direction=Direction.FORWARD, skip_children=False):
		u"""
		Focus next or previous heading in the given direction

		:direction: True for next heading, False for previous heading
		:returns: next heading or None
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		heading = current_heading
		focus_heading = None
		# FIXME this is just a piece of really ugly and unmaintainable code. It
		# should be rewritten
		if not heading:
			if direction == Direction.FORWARD and d.headings \
					and vim.current.window.cursor[0] < d.headings[0].start_vim:
				# the cursor is in the meta information are, therefore focus
				# first heading
				focus_heading = d.headings[0]
			if not (heading or focus_heading):
				if mode == u'visual':
					# restore visual selection when no heading was found
					vim.command(u'normal! gv'.encode(u'utf-8'))
				else:
					echo(u'No heading found')
				return
		elif direction == Direction.BACKWARD:
			if vim.current.window.cursor[0] != heading.start_vim:
				# the cursor is in the body of the current heading, therefore
				# the current heading will be focused
				if mode == u'visual':
					line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
					line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]
					if line_start >= heading.start_vim and line_end > heading.start_vim:
						focus_heading = heading
				else:
					focus_heading = heading

		# so far no heading has been found that the next focus should be on
		if not focus_heading:
			if not skip_children and direction == Direction.FORWARD and heading.children:
				focus_heading = heading.children[0]
			elif direction == Direction.FORWARD and heading.next_sibling:
				focus_heading = heading.next_sibling
			elif direction == Direction.BACKWARD and heading.previous_sibling:
				focus_heading = heading.previous_sibling
				if not skip_children:
					while focus_heading.children:
						focus_heading = focus_heading.children[-1]
			else:
				if direction == Direction.FORWARD:
					focus_heading = current_heading.next_heading
				else:
					focus_heading = current_heading.previous_heading

		noheadingfound = False
		if not focus_heading:
			if mode in (u'visual', u'operator'):
				# the cursor seems to be on the last or first heading of this
				# document and performes another next/previous operation
				focus_heading = heading
				noheadingfound = True
			else:
				if direction == Direction.FORWARD:
					echo(u'Already focussing last heading')
				else:
					echo(u'Already focussing first heading')
				return

		if mode == u'visual':
			cls._change_visual_selection(current_heading, focus_heading, direction=direction, noheadingfound=noheadingfound)
		elif mode == u'operator':
			if direction == Direction.FORWARD and vim.current.window.cursor[0] >= focus_heading.start_vim:
				vim.current.window.cursor = (focus_heading.end_vim, len(vim.current.buffer[focus_heading.end].decode(u'utf-8')))
			else:
				vim.current.window.cursor = (focus_heading.start_vim, 0)
		else:
			vim.current.window.cursor = (focus_heading.start_vim, focus_heading.level + 1)
		if noheadingfound:
			return
		return focus_heading

	@classmethod
	@apply_count
	def previous(cls, mode, skip_children=False):
		u"""
		Focus previous heading
		"""
		return cls._focus_heading(mode, direction=Direction.BACKWARD, skip_children=skip_children)

	@classmethod
	@apply_count
	def next(cls, mode, skip_children=False):
		u"""
		Focus next heading
		"""
		return cls._focus_heading(mode, direction=Direction.FORWARD, skip_children=skip_children)

	def register(self):
		# normal mode
		self.keybindings.append(Keybinding(u'g{', Plug('OrgJumpToParentNormal', u':py ORGMODE.plugins[u"Navigator"].parent(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Up', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingNormal', u':py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Down', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousNormal', u':py ORGMODE.plugins[u"Navigator"].previous(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Previous', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextNormal', u':py ORGMODE.plugins[u"Navigator"].next(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Next', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding(u'g{', Plug(u'OrgJumpToParentVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].parent(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"visual")<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding(u'g{', Plug(u'OrgJumpToParentOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].parent(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"operator")<CR>', mode=MODE_OPERATOR)))

		# section wise movement (skip children)
		# normal mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenNormal', u':py ORGMODE.plugins[u"Navigator"].previous(mode=u"normal", skip_children=True)<CR>')))
		self.menu + ActionEntry(u'Ne&xt Same Level', self.keybindings[-1])
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenNormal', u':py ORGMODE.plugins[u"Navigator"].next(mode=u"normal", skip_children=True)<CR>')))
		self.menu + ActionEntry(u'Pre&vious Same Level', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"visual", skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"visual", skip_children=True)<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
ftplugin/orgmode/plugins/ShowHide.py	[[[1
125
# -*- coding: utf-8 -*-

from orgmode import settings
from orgmode import ORGMODE, apply_count
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_NORMAL

import vim

class ShowHide(object):
	u""" Show Hide plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&Show Hide')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	@apply_count
	def toggle_folding(cls, reverse=False):
		u""" Toggle folding similar to the way orgmode does

		This is just a convenience function, don't hesitate to use the z*
		keybindings vim offers to deal with folding!

		:reverse:	If False open folding by one level otherwise close it by one.
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			vim.eval(u'feedkeys("<Tab>", "n")'.encode(u'utf-8'))
			return

		cursor = vim.current.window.cursor[:]

		if int(vim.eval((u'foldclosed(%d)' % heading.start_vim).encode(u'utf-8'))) != -1:
			if not reverse:
				# open closed fold
				p = heading.number_of_parents
				if not p:
					p = heading.level
				vim.command((u'normal! %dzo' % p).encode(u'utf-8'))
			else:
				# reverse folding opens all folds under the cursor
				vim.command((u'%d,%dfoldopen!' % (heading.start_vim, heading.end_of_last_child_vim)).encode(u'utf-8'))
			vim.current.window.cursor = cursor
			return heading

		def fold_depth(h):
			if int(vim.eval((u'foldclosed(%d)' % h.start_vim).encode(u'utf-8'))) != -1:
				return (h.number_of_parents, True)
			else:
				res = [h.number_of_parents + 1]
				found = False

				for c in h.children:
					d, f = fold_depth(c)
					res.append(d)
					found |= f

				return (max(res), found)

		def open_fold(h):
			if h.number_of_parents <= open_depth:
				vim.command((u'normal! %dgg%dzo' % (h.start_vim, open_depth)).encode(u'utf-8'))
			for c in h.children:
				open_fold(c)

		def close_fold(h):
			for c in h.children:
				close_fold(c)
			if h.number_of_parents >= open_depth - 1 and \
					int(vim.eval((u'foldclosed(%d)' % h.start_vim).encode(u'utf-8'))) == -1:
				vim.command((u'normal! %dggzc' % (h.start_vim, )).encode(u'utf-8'))

		# find deepest fold
		open_depth, found_fold = fold_depth(heading)

		if not reverse:
			# recursively open folds
			if found_fold:
				for child in heading.children:
					open_fold(child)
			else:
				vim.command((u'%d,%dfoldclose!' % (heading.start_vim, heading.end_of_last_child_vim)).encode(u'utf-8'))

				if heading.number_of_parents:
					# restore cursor position, it might have been changed by open_fold
					vim.current.window.cursor = cursor

					p = heading.number_of_parents
					if not p:
						p = heading.level
					# reopen fold again beacause the former closing of the fold closed all levels, including parents!
					vim.command((u'normal! %dzo' % (p, )).encode(u'utf-8'))
		else:
			# close the last level of folds
			close_fold(heading)

		# restore cursor position
		vim.current.window.cursor = cursor
		return heading

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# register plug

		self.keybindings.append(Keybinding(u'<Tab>', Plug(u'OrgToggleFoldingNormal', u':py ORGMODE.plugins[u"ShowHide"].toggle_folding()<CR>')))
		self.menu + ActionEntry(u'&Cycle Visibility', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Tab>', Plug(u'OrgToggleFoldingReverse', u':py ORGMODE.plugins[u"ShowHide"].toggle_folding(reverse=True)<CR>')))
		self.menu + ActionEntry(u'Cycle Visibility &Reverse', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>,', u'zr', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'<localleader>.', u'zm', mode=MODE_NORMAL))
		for i in xrange(0, 10):
			self.keybindings.append(Keybinding(u'<localleader>%d' % (i, ), u'zM:set fdl=%d<CR>' % i, mode=MODE_NORMAL))
ftplugin/orgmode/plugins/EditStructure.py	[[[1
373
# -*- coding: utf-8 -*-

from orgmode import ORGMODE, apply_count, repeat, realign_tags
from orgmode import settings
from orgmode.exceptions import HeadingDomError
from orgmode.keybinding import Keybinding, Plug, MODE_INSERT, MODE_NORMAL
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.liborgmode.base import Direction
from orgmode.liborgmode.headings import Heading

import vim

class EditStructure(object):
	u""" EditStructure plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&Edit Structure')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def new_heading(cls, below=None, insert_mode=False, end_of_last_child=False):
		u"""
		:below:				True, insert heading below current heading, False,
							insert heading above current heading, None, special
							behavior for insert mode, use the current text as
							heading
		:insert_mode:		True, if action is performed in insert mode
		:end_of_last_child:	True, insert heading at the end of last child,
							otherwise the newly created heading will "take
							over" the current heading's children
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		cursor = vim.current.window.cursor[:]
		if not current_heading:
			# the user is in meta data region
			pos = cursor[0] - 1
			heading = Heading(title=d.meta_information[pos], body=d.meta_information[pos + 1:])
			d.headings.insert(0, heading)
			del d.meta_information[pos:]
			d.write()
			vim.command((u'exe "normal %dgg"|startinsert!' % (heading.start_vim, )).encode(u'utf-8'))
			return heading

		heading = Heading(level=current_heading.level)

		# it's weird but this is the behavior of original orgmode
		if below is None:
			below = cursor[1] != 0 or end_of_last_child

		# insert newly created heading
		l = current_heading.get_parent_list()
		idx = current_heading.get_index_in_parent_list()
		if l is not None and idx is not None:
			l.insert(idx + (1 if below else 0), heading)
		else:
			raise HeadingDomError(u'Current heading is not properly linked in DOM')

		if below and not end_of_last_child:
			# append heading at the end of current heading but also take
			# over the children of current heading
			#heading.children = [h.copy() for h in current_heading.children]
			#del current_heading.children
			heading._children.data = current_heading._children.data[:]
			del current_heading._children.data[:]
			for h in heading._children.data:
				h._parent = heading

		# if cursor is currently on a heading, insert parts of it into the
		# newly created heading
		if insert_mode and cursor[1] != 0 and cursor[0] == current_heading.start_vim:
			offset = cursor[1] - current_heading.level - 1 - (len(current_heading.todo) \
					+ 1 if current_heading.todo else 0)
			if offset < 0:
				offset = 0
			if int(settings.get(u'org_improve_split_heading', u'1')) and \
					offset > 0 and len(current_heading.title) == offset + 1 \
					and current_heading.title[offset - 1] not in (u' ', u'\t'):
				offset += 1
			heading.title = current_heading.title[offset:]
			current_heading.title = current_heading.title[:offset]
			heading.body = current_heading.body[:]
			current_heading.body = []

		d.write()
		vim.command((u'exe "normal %dgg"|startinsert!' % (heading.start_vim, )).encode(u'utf-8'))

		# return newly created heading
		return heading

	@classmethod
	def _change_heading_level(cls, level, including_children=True, on_heading=False, insert_mode=False):
		u"""
		Change level of heading realtively with or without including children.

		:level:					the number of levels to promote/demote heading
		:including_children:	True if should should be included in promoting/demoting
		:on_heading:			True if promoting/demoting should only happen when the cursor is on the heading
		:insert_mode:			True if vim is in insert mode
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		if not current_heading or on_heading and current_heading.start_vim != vim.current.window.cursor[0]:
			# TODO figure out the actually pressed keybinding and feed these
			# keys instead of making keys up like this
			if level > 0:
				if insert_mode:
					vim.eval(u'feedkeys("\<C-t>", "n")'.encode(u'utf-8'))
				elif including_children:
					vim.eval(u'feedkeys(">]]", "n")'.encode(u'utf-8'))
				elif on_heading:
					vim.eval(u'feedkeys(">>", "n")'.encode(u'utf-8'))
				else:
					vim.eval(u'feedkeys(">}", "n")'.encode(u'utf-8'))
			else:
				if insert_mode:
					vim.eval(u'feedkeys("\<C-d>", "n")'.encode(u'utf-8'))
				elif including_children:
					vim.eval(u'feedkeys("<]]", "n")'.encode(u'utf-8'))
				elif on_heading:
					vim.eval(u'feedkeys("<<", "n")'.encode(u'utf-8'))
				else:
					vim.eval(u'feedkeys("<}", "n")'.encode(u'utf-8'))
			# return True because otherwise apply_count will not work
			return True

		# don't allow demotion below level 1
		if current_heading.level == 1 and level < 1:
			return False

		# reduce level of demotion to a minimum heading level of 1
		if (current_heading.level + level) < 1:
			level = 1

		def indent(heading, ic):
			if not heading:
				return
			heading.level += level

			if ic:
				for child in heading.children:
					indent(child, ic)

		# save cursor position
		c = vim.current.window.cursor[:]

		# indent the promoted/demoted heading
		indent_end_vim = current_heading.end_of_last_child_vim if including_children else current_heading.end_vim
		indent(current_heading, including_children)

		# when changing the level of a heading, its position in the DOM
		# needs to be updated. It's likely that the heading gets a new
		# parent and new children when demoted or promoted

		# find new parent
		p = current_heading.parent
		pl = current_heading.get_parent_list()
		ps = current_heading.previous_sibling
		nhl = current_heading.level

		def append_heading(heading, parent):
			if heading.level <= parent.level:
				raise ValueError('Heading level not is lower than parent level: %d ! > %d' % (heading.level, parent.level))

			if parent.children and parent.children[-1].level < heading.level:
				append_heading(heading, parent.children[-1])
			else:
				parent.children.append(heading)

		if level > 0:
			# demotion
			# subheading or top level heading
			if ps and nhl > ps.level:
				idx = current_heading.get_index_in_parent_list()
				pl.remove(current_heading)
				# find heading that is the new parent heading
				oh = ps
				h = ps
				while nhl > h.level:
					oh = h
					if h.children:
						h = h.children[-1]
					else:
						break
				np = h if nhl > h.level else oh

				# append current heading to new heading
				np.children.append(current_heading)

				# if children are not included, distribute them among the
				# parent heading and it's siblings
				if not including_children:
					for h in current_heading.children[:]:
						if h and h.level <= nhl:
							append_heading(h.copy(), np if np else p)
							current_heading.children.remove(h)
		else:
			# promotion
			if p and nhl <= p.level:
				idx = current_heading.get_index_in_parent_list() + 1
				# find the new parent heading
				oh = p
				h = p
				while nhl <= h.level:
					# append new children to current heading
					[ append_heading(child.copy(), current_heading) for child in h.children[idx:] ]
					del h.children[idx:]
					oh = h
					idx = h.get_index_in_parent_list() + 1
					if h.parent:
						h = h.parent
					else:
						break
				ns = oh.next_sibling
				while ns and ns.level > current_heading.level:
					nns = ns.next_sibling
					append_heading(ns, current_heading)
					ns = nns

				# append current heading to new parent heading / document
				pl.remove(current_heading)
				if nhl > h.level:
					h.children.insert(idx, current_heading)
				else:
					d.headings.insert(idx, current_heading)

		d.write()
		if indent_end_vim != current_heading.start_vim:
			vim.command((u'normal %dggV%dgg=' % (current_heading.start_vim, indent_end_vim)).encode(u'utf-8'))
		# restore cursor position
		vim.current.window.cursor = (c[0], c[1] + level)

		return True

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def demote_heading(cls, including_children=True, on_heading=False, insert_mode=False):
		if cls._change_heading_level(1, including_children=including_children, on_heading=on_heading, insert_mode=insert_mode):
			if including_children:
				return u'OrgDemoteSubtree'
			return u'OrgDemoteHeading'

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def promote_heading(cls, including_children=True, on_heading=False, insert_mode=False):
		if cls._change_heading_level(-1, including_children=including_children, on_heading=on_heading, insert_mode=insert_mode):
			if including_children:
				return u'OrgPromoteSubtreeNormal'
			return u'OrgPromoteHeadingNormal'

	@classmethod
	def _move_heading(cls, direction=Direction.FORWARD, including_children=True):
		u""" Move heading up or down

		:returns: heading or None
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if (not heading) or \
				(direction == Direction.FORWARD and not heading.next_sibling) or \
				(direction == Direction.BACKWARD and not heading.previous_sibling):
			return None

		cursor_offset_within_the_heading_vim = vim.current.window.cursor[0] - (heading._orig_start + 1)

		if not including_children:
			heading.previous_sibling.children.extend(heading.children)
			del heading.children

		heading_insert_position = 0 if direction == Direction.FORWARD else -1
		l = heading.get_parent_list()
		idx = heading.get_index_in_parent_list()
		del l[idx]
		if l is not None and idx is not None:
			l.insert(idx + heading_insert_position, heading)
		else:
			raise HeadingDomError(u'Current heading is not properly linked in DOM')

		d.write()

		vim.current.window.cursor = (heading.start_vim + cursor_offset_within_the_heading_vim, vim.current.window.cursor[1])

		return True

	@classmethod
	@repeat
	@apply_count
	def move_heading_upward(cls, including_children=True):
		if cls._move_heading(direction=Direction.BACKWARD, including_children=including_children):
			return u'OrgMoveHeadingUpward'

	@classmethod
	@repeat
	@apply_count
	def move_heading_downward(cls, including_children=True):
		if cls._move_heading(direction=Direction.FORWARD, including_children=including_children):
			return u'OrgMoveHeadingDownward'

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		settings.set(u'org_improve_split_heading', u'1')

		self.keybindings.append(Keybinding(u'<C-S-CR>', Plug(u'OrgNewHeadingAboveNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].new_heading(below=False)<CR>')))
		self.menu + ActionEntry(u'New Heading &above', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'<S-CR>', Plug(u'OrgNewHeadingBelowNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].new_heading(below=True)<CR>')))
		self.menu + ActionEntry(u'New Heading &below', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'<C-CR>', Plug(u'OrgNewHeadingBelowAfterChildrenNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].new_heading(below=True, end_of_last_child=True)<CR>')))
		self.menu + ActionEntry(u'New Heading below, after &children', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-CR>', Plug(u'OrgNewHeadingAboveInsert', u'<C-o>:<C-u>silent! py ORGMODE.plugins[u"EditStructure"].new_heading(below=False, insert_mode=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding(u'<S-CR>', Plug(u'OrgNewHeadingBelowInsert', u'<C-o>:<C-u>silent! py ORGMODE.plugins[u"EditStructure"].new_heading(insert_mode=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding(u'<C-CR>', Plug(u'OrgNewHeadingBelowAfterChildrenInsert', u'<C-o>:<C-u>silent! py ORGMODE.plugins[u"EditStructure"].new_heading(insert_mode=True, end_of_last_child=True)<CR>', mode=MODE_INSERT)))

		self.menu + Separator()

		self.keybindings.append(Keybinding(u'm{', Plug(u'OrgMoveHeadingUpward', u':py ORGMODE.plugins[u"EditStructure"].move_heading_upward(including_children=False)<CR>')))
		self.keybindings.append(Keybinding(u'm[[', Plug(u'OrgMoveSubtreeUpward', u':py ORGMODE.plugins[u"EditStructure"].move_heading_upward()<CR>')))
		self.menu + ActionEntry(u'Move Subtree &Up', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'm}', Plug(u'OrgMoveHeadingDownward', u':py ORGMODE.plugins[u"EditStructure"].move_heading_downward(including_children=False)<CR>')))
		self.keybindings.append(Keybinding(u'm]]', Plug(u'OrgMoveSubtreeDownward', u':py ORGMODE.plugins[u"EditStructure"].move_heading_downward()<CR>')))
		self.menu + ActionEntry(u'Move Subtree &Down', self.keybindings[-1])

		self.menu + Separator()

		self.menu + ActionEntry(u'&Copy Heading', u'yah', u'yah')
		self.menu + ActionEntry(u'C&ut Heading', u'dah', u'dah')

		self.menu + Separator()

		self.menu + ActionEntry(u'&Copy Subtree', u'yar', u'yar')
		self.menu + ActionEntry(u'C&ut Subtree', u'dar', u'dar')
		self.menu + ActionEntry(u'&Paste Subtree', u'p', u'p')

		self.menu + Separator()

		self.keybindings.append(Keybinding(u'<ah', Plug(u'OrgPromoteHeadingNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].promote_heading(including_children=False)<CR>')))
		self.menu + ActionEntry(u'&Promote Heading', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'<<', Plug(u'OrgPromoteOnHeadingNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].promote_heading(including_children=False, on_heading=True)<CR>')))
		self.keybindings.append(Keybinding(u'<{', u'<Plug>OrgPromoteHeadingNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'<ih', u'<Plug>OrgPromoteHeadingNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding(u'<ar', Plug(u'OrgPromoteSubtreeNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].promote_heading()<CR>')))
		self.menu + ActionEntry(u'&Promote Subtree', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'<[[', u'<Plug>OrgPromoteSubtreeNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'<ir', u'<Plug>OrgPromoteSubtreeNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding(u'>ah', Plug(u'OrgDemoteHeadingNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].demote_heading(including_children=False)<CR>')))
		self.menu + ActionEntry(u'&Demote Heading', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'>>', Plug(u'OrgDemoteOnHeadingNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].demote_heading(including_children=False, on_heading=True)<CR>')))
		self.keybindings.append(Keybinding(u'>}', u'>Plug>OrgDemoteHeadingNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'>ih', u'>Plug>OrgDemoteHeadingNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding(u'>ar', Plug(u'OrgDemoteSubtreeNormal', u':silent! py ORGMODE.plugins[u"EditStructure"].demote_heading()<CR>')))
		self.menu + ActionEntry(u'&Demote Subtree', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'>]]', u'<Plug>OrgDemoteSubtreeNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'>ir', u'<Plug>OrgDemoteSubtreeNormal', mode=MODE_NORMAL))

		# other keybindings
		self.keybindings.append(Keybinding(u'<C-d>', Plug(u'OrgPromoteOnHeadingInsert', u'<C-o>:silent! py ORGMODE.plugins[u"EditStructure"].promote_heading(including_children=False, on_heading=True, insert_mode=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding(u'<C-t>', Plug(u'OrgDemoteOnHeadingInsert', u'<C-o>:silent! py ORGMODE.plugins[u"EditStructure"].demote_heading(including_children=False, on_heading=True, insert_mode=True)<CR>', mode=MODE_INSERT)))
ftplugin/orgmode/liborgmode/documents.py	[[[1
318
# -*- coding: utf-8 -*-

"""
	documents
	~~~~~~~~~

	TODO: explain this :)
"""

from UserList import UserList

from orgmode.liborgmode.base import MultiPurposeList, flatten_list, Direction
from orgmode.liborgmode.headings import Heading, HeadingList


class Document(object):
	u"""
	Representation of a whole org-mode document.

	A Document consists basically of headings (see Headings) and some metadata.

	TODO: explain the 'dirty' mechanism
	"""

	def __init__(self):
		u"""
		Don't call this constructor directly but use one of the concrete
		implementations.

		TODO: what are the concrete implementatiions?
		"""
		object.__init__(self)

		# is a list - only the Document methods should work with this list!
		self._content = None
		self._dirty_meta_information = False
		self._dirty_document = False
		self._meta_information = MultiPurposeList(on_change = self.set_dirty_meta_information)
		self._orig_meta_information_len = None
		self._headings = HeadingList(obj=self)
		self._deleted_headings = []

		# settings needed to align tags properly
		self._tabstop = 8
		self._tag_column = 77

		self.todo_states = [u'TODO', u'DONE']

	def __unicode__(self):
		if self.meta_information is None:
			return '\n'.join(self.all_headings())
		return '\n'.join(self.meta_information) + '\n' + '\n'.join(['\n'.join([unicode(i)] + i.body) for i in self.all_headings()])

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def get_all_todo_states(self):
		u""" Convenience function that returns all todo and done states and
		sequences in one big list.

		:returns:	[all todo/done states]
		"""
		return flatten_list(self.get_todo_states())

	def get_todo_states(self):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		:returns:	[([todo states], [done states]), ..]
		"""
		return self.todo_states

	def tabstop():
		u""" Tabstop for this document """
		def fget(self):
			return self._tabstop

		def fset(self, value):
			self._tabstop = value

		return locals()
	tabstop = property(**tabstop())

	def tag_column():
		u""" The column all tags are right-aligned to """
		def fget(self):
			return self._tag_column

		def fset(self, value):
			self._tag_column = value

		return locals()
	tag_column = property(**tag_column())

	def init_dom(self, heading=Heading):
		u""" Initialize all headings in document - build DOM. This method
		should be call prior to accessing the document.

		:returns:	self
		"""
		def init_heading(_h):
			u"""
			:returns	the initialized heading
			"""
			start = _h.end + 1
			prev_heading = None
			while True:
				new_heading = self.find_heading(start, heading=heading)

				# * Heading 1 <- heading
				# * Heading 1 <- sibling
				# or
				# * Heading 2 <- heading
				# * Heading 1 <- parent's sibling
				if not new_heading or \
						new_heading.level <= _h.level:
					break

				# * Heading 1 <- heading
				#  * Heading 2 <- first child
				#  * Heading 2 <- another child
				new_heading._parent = _h
				if prev_heading:
					prev_heading._next_sibling = new_heading
					new_heading._previous_sibling = prev_heading
				_h.children.data.append(new_heading)
				# the start and end computation is only
				# possible when the new heading was properly
				# added to the document structure
				init_heading(new_heading)
				if new_heading.children:
					# skip children
					start = new_heading.end_of_last_child + 1
				else:
					start = new_heading.end + 1
				prev_heading = new_heading

			return _h

		h = self.find_heading(heading=heading)
		# initialize meta information
		if h:
			self._meta_information.data.extend(self._content[:h._orig_start])
		else:
			self._meta_information.data.extend(self._content[:])
		self._orig_meta_information_len = len(self.meta_information)

		# initialize dom tree
		prev_h = None
		while h:
			if prev_h:
				prev_h._next_sibling = h
				h._previous_sibling = prev_h
			self.headings.data.append(h)
			init_heading(h)
			prev_h = h
			h = self.find_heading(h.end_of_last_child + 1, heading=heading)

		return self

	def meta_information():
		u"""
		Meta information is text that precedes all headings in an org-mode
		document. It might contain additional information about the document,
		e.g. author
		"""
		def fget(self):
			return self._meta_information

		def fset(self, value):
			if self._orig_meta_information_len is None:
				self._orig_meta_information_len = len(self.meta_information)
			if type(value) in (list, tuple) or isinstance(value, UserList):
				self._meta_information[:] = flatten_list(value)
			elif type(value) in (str, ):
				self._meta_information[:] = value.decode(u'utf-8').split(u'\n')
			elif type(value) in (unicode, ):
				self._meta_information[:] = value.split(u'\n')
			self.set_dirty_meta_information()

		def fdel(self):
			self.meta_information = u''

		return locals()
	meta_information = property(**meta_information())

	def headings():
		u""" List of top level headings """
		def fget(self):
			return self._headings

		def fset(self, value):
			self._headings[:] = value

		def fdel(self):
			del self.headings[:]

		return locals()
	headings = property(**headings())

	def write(self):
		u""" write the document

		:returns:	True if something was written, otherwise False
		"""
		raise NotImplementedError(u'Abstract method, please use concrete impelementation!')

	def set_dirty_meta_information(self):
		u""" Mark the meta information dirty so that it will be rewritten when
		saving the document """
		self._dirty_meta_information = True

	def set_dirty_document(self):
		u""" Mark the whole document dirty. When changing a heading this
		method must be executed in order to changed computation of start and
		end positions from a static to a dynamic computation """
		self._dirty_document = True

	@property
	def is_dirty(self):
		u"""
		Return information about unsaved changes for the document and all
		related headings.

		:returns:	 Return True if document contains unsaved changes.
		"""
		if self.is_dirty_meta_information:
			return True

		if self.is_dirty_document:
			return True

		if self._deleted_headings:
			return True

		return False

	@property
	def is_dirty_meta_information(self):
		u""" Return True if the meta information is marked dirty """
		return self._dirty_meta_information

	@property
	def is_dirty_document(self):
		u""" Return True if the document is marked dirty """
		return self._dirty_document

	def all_headings(self):
		u""" Iterate over all headings of the current document in serialized
		order

		:returns:	Returns an iterator object which returns all headings of
					the current file in serialized order
		"""
		if not self.headings:
			raise StopIteration()

		h = self.headings[0]
		while h:
			yield h
			h = h.next_heading
		raise StopIteration()

	def find_heading(self, position=0, direction=Direction.FORWARD, \
			heading=Heading, connect_with_document=True):
		u""" Find heading in the given direction

		:postition: starting line, counting from 0 (in vim you start
				counting from 1, don't forget)
		:direction: downwards == Direction.FORWARD,
				upwards == Direction.BACKWARD
		:heading:   Heading class from which new heading objects will be
				instanciated
		:connect_with_document: if True, the newly created heading will be
				connected with the document, otherwise not

		:returns:	New heading object or None
		"""
		len_cb = len(self._content)

		if position < 0 or position > len_cb:
			return

		tmp_line = position
		start = None
		end = None

		# Search heading upwards
		if direction == Direction.FORWARD:
			while tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) is not None:
					if start is None:
						start = tmp_line
					elif end is None:
						end = tmp_line - 1
					if start is not None and end is not None:
						break
				tmp_line += 1
		else:
			while tmp_line >= 0 and tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) is not None:
					if start is None:
						start = tmp_line
					elif end is None:
						end = tmp_line - 1
					if start is not None and end is not None:
						break
				tmp_line -= 1 if start is None else -1

		if start is not None and end is None:
			end = len_cb - 1
		if start is not None and end is not None:
			return heading.parse_heading_from_data(self._content[start:end + 1], self.get_all_todo_states(), \
					document=self if connect_with_document else None, orig_start=start)


# vim: set noexpandtab:
ftplugin/orgmode/liborgmode/agendafilter.py	[[[1
79
# -*- coding: utf-8 -*-

u"""
	agendafilter
	~~~~~~~~~~~~~~~~

	AgendaFilter contains all the filters that can be applied to create the
	agenda.


	All functions except filter_items() in the module are filters. Given a
	heading they return if the heading meets the critera of the filter.

	The function filter_items() can combine different filters and only returns
	the filtered headings.
"""

from datetime import date
from datetime import datetime
from datetime import timedelta


def filter_items(headings, filters):
	u"""
	Filter the given headings. Return the list of headings which were not
	filtered.

	:headings: is an list of headings
	:filters: is the list of filters that are to be applied. all function in
			this module (except this function) are filters.

	You can use it like this:

	>>> filtered = filter_items(headings, [contains_active_date,
				contains_active_todo])

	"""
	filtered = headings
	for f in filters:
		filtered = filter(f, filtered)
	return filtered


def is_within_week(heading):
	u"""
	Return True if the date in the deading is within a week in the future (or
	older.
	"""
	if contains_active_date(heading):
		next_week = datetime.today() + timedelta(days=7)
		if heading.active_date < next_week:
			return True


def is_within_week_and_active_todo(heading):
	u"""
	Return True if heading contains an active TODO and the date is within a
	week.
	"""
	return is_within_week(heading) and contains_active_todo(heading)


def contains_active_todo(heading):
	u"""
	Return True if heading contains an active TODO.

	FIXME: the todo checking should consider a number of different active todo
	states
	"""
	return heading.todo == u"TODO"


def contains_active_date(heading):
	u"""
	Return True if heading contains an active date.
	"""
	return not(heading.active_date is None)

# vim: set noexpandtab:
ftplugin/orgmode/liborgmode/orgdate.py	[[[1
277
# -*- coding: utf-8 -*-
u"""
	OrgDate
	~~~~~~~~~~~~~~~~~~

	This module contains all date/time/timerange representations that exist in
	orgmode.

	There exist three different kinds:

	* OrgDate: is similar to a date object in python and it looks like
	  '2011-09-07 Wed'.

	* OrgDateTime: is similar to a datetime object in python and looks like
	  '2011-09-07 Wed 10:30'

	* OrgTimeRange: indicates a range of time. It has a start and and end date:
	  * <2011-09-07 Wed>--<2011-09-08 Fri>
	  * <2011-09-07 Wed 10:00-13:00>

	All OrgTime oblects can be active or inactive.
"""

import datetime
import re

# <2011-09-12 Mon>
_DATE_REGEX = re.compile(r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>")
# [2011-09-12 Mon]
_DATE_PASSIVE_REGEX = re.compile(r"\[(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w\]")

# <2011-09-12 Mon 10:20>
_DATETIME_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d{1,2}):(\d\d)>")
# [2011-09-12 Mon 10:20]
_DATETIME_PASSIVE_REGEX = re.compile(
		r"\[(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d{1,2}):(\d\d)\]")

# <2011-09-12 Mon>--<2011-09-13 Tue>
_DATERANGE_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>--<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>")
# <2011-09-12 Mon 10:00>--<2011-09-12 Mon 11:00>
_DATETIMERANGE_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)>--<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)>")
# <2011-09-12 Mon 10:00--12:00>
_DATETIMERANGE_SAME_DAY_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)-(\d\d):(\d\d)>")


def get_orgdate(data):
	u"""
	Parse the given data (can be a string or list). Return an OrgDate if data
	contains a string representation of an OrgDate; otherwise return None.

	data can be a string or a list containing strings.
	"""
	if isinstance(data, list):
		return _findfirst(_text2orgdate, data)
	else:
		return _text2orgdate(data)
	# if no dates found
	return None


def _findfirst(f, seq):
	u"""
	Return first item in sequence seq where f(item) == True.

	TODO: this is a general help function and it should be moved somewhere
	else; preferably into the standard lib :)
	"""
	for found in (f(item) for item in seq if f(item)):
		return found


def _text2orgdate(string):
	u"""
	Transform the given string into an OrgDate.
	Return an OrgDate if data contains a string representation of an OrgDate;
	otherwise return None.
	"""
	# handle active datetime with same day
	result = _DATETIMERANGE_SAME_DAY_REGEX.search(string)
	if result:
		try:
			(syear, smonth, sday, shour, smin, ehour, emin) = \
					[int(m) for m in result.groups()]
			start = datetime.datetime(syear, smonth, sday, shour, smin)
			end = datetime.datetime(syear, smonth, sday, ehour, emin)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATETIMERANGE_REGEX.search(string)
	if result:
		try:
			(syear, smonth, sday, shour, smin,
					eyear, emonth, eday, ehour, emin) = [int(m) for m in result.groups()]
			start = datetime.datetime(syear, smonth, sday, shour, smin)
			end = datetime.datetime(eyear, emonth, eday, ehour, emin)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATERANGE_REGEX.search(string)
	if result:
		try:
			syear, smonth, sday, eyear, emonth, ehour = [int(m) for m in result.groups()]
			start = datetime.date(syear, smonth, sday)
			end = datetime.date(eyear, emonth, ehour)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATETIME_REGEX.search(string)
	if result:
		try:
			year, month, day, hour, minutes = [int(m) for m in result.groups()]
			return OrgDateTime(True, year, month, day, hour, minutes)
		except Exception:
			return None

	# handle passive datetime
	result = _DATETIME_PASSIVE_REGEX.search(string)
	if result:
		try:
			year, month, day, hour, minutes = [int(m) for m in result.groups()]
			return OrgDateTime(False, year, month, day, hour, minutes)
		except Exception:
			return None

	# handle passive dates
	result = _DATE_PASSIVE_REGEX.search(string)
	if result:
		try:
			year, month, day = [int(m) for m in result.groups()]
			return OrgDate(False, year, month, day)
		except Exception:
			return None

	# handle active dates
	result = _DATE_REGEX.search(string)
	if result:
		try:
			year, month, day = [int(m) for m in result.groups()]
			return OrgDate(True, year, month, day)
		except Exception:
			return None


class OrgDate(datetime.date):
	u"""
	OrgDate represents a normal date like '2011-08-29 Mon'.

	OrgDates can be active or inactive.

	NOTE: date is immutable. Thats why there needs to be __new__().
	See: http://docs.python.org/reference/datamodel.html#object.__new__
	"""
	def __init__(self, active, year, month, day):
		self.active = active
		pass

	def __new__(cls, active, year, month, day):
		return datetime.date.__new__(cls, year, month, day)

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		if self.active:
			return self.strftime(u'<%Y-%m-%d %a>')
		else:
			return self.strftime(u'[%Y-%m-%d %a]')

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')


class OrgDateTime(datetime.datetime):
	u"""
	OrgDateTime represents a normal date like '2011-08-29 Mon'.

	OrgDateTime can be active or inactive.

	NOTE: date is immutable. Thats why there needs to be __new__().
	See: http://docs.python.org/reference/datamodel.html#object.__new__
	"""

	def __init__(self, active, year, month, day, hour, mins):
		self.active = active

	def __new__(cls, active, year, month, day, hour, minute):
		return datetime.datetime.__new__(cls, year, month, day, hour, minute)

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		if self.active:
			return self.strftime(u'<%Y-%m-%d %a %H:%M>')
		else:
			return self.strftime(u'[%Y-%m-%d %a %H:%M]')

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')


class OrgTimeRange(object):
	u"""
	OrgTimeRange objects have a start and an end. Start and ent can be date
	or datetime. Start and end have to be the same type.

	OrgTimeRange objects look like this:
	* <2011-09-07 Wed>--<2011-09-08 Fri>
	* <2011-09-07 Wed 20:00>--<2011-09-08 Fri 10:00>
	* <2011-09-07 Wed 10:00-13:00>
	"""

	def __init__(self, active, start, end):
		u"""
		stat and end must be datetime.date or datetime.datetime (both of the
		same type).
		"""
		super(OrgTimeRange, self).__init__()
		self.start = start
		self.end = end
		self.active = active

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		# active
		if self.active:
			# datetime
			if isinstance(self.start, datetime.datetime):
				# if start and end are on same the day
				if self.start.year == self.end.year and\
						self.start.month == self.end.month and\
						self.start.day == self.end.day:
					return u"<%s-%s>" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%H:%M'))
				else:
					return u"<%s>--<%s>" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%Y-%m-%d %a %H:%M'))
			# date
			if isinstance(self.start, datetime.date):
				return u"<%s>--<%s>" % (self.start.strftime(u'%Y-%m-%d %a'),
						self.end.strftime(u'%Y-%m-%d %a'))
		# inactive
		else:
			if isinstance(self.start, datetime.datetime):
				# if start and end are on same the day
				if self.start.year == self.end.year and\
						self.start.month == self.end.month and\
						self.start.day == self.end.day:
					return u"[%s-%s]" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%H:%M'))
				else:
					return u"[%s]--[%s]" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%Y-%m-%d %a %H:%M'))
			if isinstance(self.start, datetime.date):
				return u"[%s]--[%s]" % (self.start.strftime(u'%Y-%m-%d %a'),
						self.end.strftime(u'%Y-%m-%d %a'))

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

# vim: set noexpandtab:
ftplugin/orgmode/liborgmode/headings.py	[[[1
870
# -*- coding: utf-8 -*-

"""
	headings
	~~~~~~~~~

	TODO: explain this :)
"""

import re
from UserList import UserList

from orgmode.liborgmode.base import MultiPurposeList, flatten_list
from orgmode.liborgmode.orgdate import OrgTimeRange
from orgmode.liborgmode.orgdate import get_orgdate


REGEX_HEADING = re.compile(
		r'^(?P<level>\*+)(\s+(?P<title>.*?))?\s*(\s(?P<tags>:[\w_:@]+:))?$',
		flags=re.U | re.L)
REGEX_TAGS = re.compile(r'^\s*((?P<title>[^\s]*?)\s+)?(?P<tags>:[\w_:@]+:)$',
		flags=re.U | re.L)
REGEX_TODO = re.compile(r'^[^\s]*$')


class Heading(object):
	u""" Structural heading object """

	def __init__(self, level=1, title=u'', tags=None, todo=None, body=None,
			active_date=None):
		u"""
		:level:		Level of the heading
		:title:		Title of the heading
		:tags:		Tags of the heading
		:todo:		Todo state of the heading
		:body:		Body of the heading
		:active_date: active date that is used in the agenda
		"""
		object.__init__(self)

		self._document = None
		self._parent = None
		self._previous_sibling = None
		self._next_sibling = None
		self._children = HeadingList(obj=self)
		self._orig_start = None
		self._orig_len = 0

		self._dirty_heading = False
		self._level = level

		# todo
		self._todo = None
		if todo:
			self.todo = todo

		# tags
		self._tags = MultiPurposeList(on_change=self.set_dirty_heading)
		if tags:
			self.tags = tags

		# title
		self._title = u''
		if title:
			self.title = title

		# body
		self._dirty_body = False
		self._body = MultiPurposeList(on_change=self.set_dirty_body)
		if body:
			self.body = body

		# active date
		self._active_date = active_date
		if active_date:
			self.active_date = active_date

	def __unicode__(self):
		res = u'*' * self.level
		if self.todo:
			res = u' '.join((res, self.todo))
		if self.title:
			res = u' '.join((res, self.title))

		# compute position of tags
		if self.tags:
			tabs = 0
			spaces = 2
			tags = (u':%s:' % (u':'.join(self.tags)))

			ts = 8
			tag_column = 77
			if self.document:
				ts = self.document.tabstop
				tag_column = self.document.tag_column

			len_heading = len(res)
			len_tags = len(tags)
			if len_heading + spaces + len_tags < tag_column:
				spaces_to_next_tabstop = ts - divmod(len_heading, ts)[1]

				if len_heading + spaces_to_next_tabstop + len_tags < tag_column:
					tabs, spaces = divmod(tag_column -
							(len_heading + spaces_to_next_tabstop + len_tags), ts)

					if spaces_to_next_tabstop:
						tabs += 1
				else:
					spaces = tag_column - (len_heading + len_tags)

			res += u'\t' * tabs + u' ' * spaces + tags

		# append a trailing space when there are just * and no text
		if len(res) == self.level:
			res += u' '
		return res

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def __len__(self):
		# 1 is for the heading's title
		return 1 + len(self.body)

	def __lt__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date < other.active_date:
				return True
			elif self.active_date == other.active_date:
				return False
			elif self.active_date > other.active_date:
				return False
		except:
			if self.active_date and not other.active_date:
				return True
			elif not self.active_date and other.active_date:
				return False
			elif not self.active_date and not other.active:
				return False

	def __le__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date < other.active_date:
				return True
			elif self.active_date == other.active_date:
				return True
			elif self.active_date > other.active_date:
				return False
		except:
			if self.active_date and not other.active_date:
				return True
			elif not self.active_date and other.active_date:
				return False
			elif not self.active_date and not other.active:
				return True

	def __ge__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date > other.active_date:
				return True
			elif self.active_date == other.active_date:
				return True
			elif self.active_date < other.active_date:
				return False
		except:
			if not self.active_date and other.active_date:
				return True
			elif self.active_date and not other.active_date:
				return False
			elif not self.active_date and not other.active:
				return True

	def __gt__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date > other.active_date:
				return True
			elif self.active_date == other.active_date:
				return False
			elif self.active_date < other.active_date:
				return False
		except:
			if not self.active_date and other.active_date:
				return True
			elif self.active_date and not other.active_date:
				return False
			elif not self.active_date and not other.active:
				return False

	def copy(self, including_children=True, parent=None):
		u"""
		Create a copy of the current heading. The heading will be completely
		detached and not even belong to a document anymore.

		:including_children:	If True a copy of all children is create as
				well. If False the returned heading doesn't have any children.
		"""
		heading = self.__class__(level=self.level, title=self.title, \
				tags=self.tags, todo=self.todo, body=self.body[:])
		if parent:
			parent.children.append(heading)
		if including_children and self.children:
			[item.copy(including_children=including_children, parent=heading) \
					for item in self.children]
		heading._orig_start = self._orig_start
		heading._orig_len = self._orig_len

		heading._dirty_heading = self.is_dirty_heading

		return heading

	@classmethod
	def parse_heading_from_data(cls, data, allowed_todo_states, document=None,
			orig_start=None):
		u""" Construct a new heading from the provided data

		:data:			List of lines
		:allowed_todo_states: TODO???
		:document:		The document object this heading belongs to
		:orig_start:	The original start of the heading in case it was read
						from a document. If orig_start is provided, the
						resulting heading will not be marked dirty.

		:returns:	The newly created heading
		"""
		def parse_title(heading_line):
			# WARNING this regular expression fails if there is just one or no
			# word in the heading but a tag!
			m = REGEX_HEADING.match(heading_line)
			if m:
				r = m.groupdict()
				level = len(r[u'level'])
				todo = None
				title = u''
				tags = filter(lambda x: x != u'', r[u'tags'].split(u':')) if r[u'tags'] else []

				# if there is just one or no word in the heading, redo the parsing
				mt = REGEX_TAGS.match(r[u'title'])
				if not tags and mt:
					r = mt.groupdict()
					tags = filter(lambda x: x != u'', r[u'tags'].split(u':')) if r[u'tags'] else []
				if r[u'title'] is not None:
					_todo_title = [i.strip() for i in r[u'title'].split(None, 1)]
					if _todo_title and _todo_title[0] in allowed_todo_states:
						todo = _todo_title[0]
						if len(_todo_title) > 1:
							title = _todo_title[1]
					else:
						title = r[u'title'].strip()

				return (level, todo, title, tags)
			raise ValueError(u'Data doesn\'t start with a heading definition.')

		if not data:
			raise ValueError(u'Unable to create heading, no data provided.')

		# create new heaing
		new_heading = cls()
		new_heading.level, new_heading.todo, new_heading.title, new_heading.tags = parse_title(data[0])
		new_heading.body = data[1:]
		if orig_start is not None:
			new_heading._dirty_heading = False
			new_heading._dirty_body = False
			new_heading._orig_start = orig_start
			new_heading._orig_len = len(new_heading)
		if document:
			new_heading._document = document

		# try to find active dates
		tmp_orgdate = get_orgdate(data)
		if tmp_orgdate and tmp_orgdate.active \
				and not isinstance(tmp_orgdate, OrgTimeRange):
			new_heading.active_date = tmp_orgdate
		else:
			new_heading.active_date = None

		return new_heading

	@classmethod
	def identify_heading(cls, line):
		u""" Test if a certain line is a heading or not.

		:line: the line to check

		:returns: level
		"""
		level = 0
		if not line:
			return None
		for i in xrange(0, len(line)):
			if line[i] == u'*':
				level += 1
				if len(line) > (i + 1) and line[i + 1] in (u'\t', u' '):
					return level
			else:
				return None

	@property
	def is_dirty(self):
		u""" Return True if the heading's body is marked dirty """
		return self._dirty_heading or self._dirty_body

	@property
	def is_dirty_heading(self):
		u""" Return True if the heading is marked dirty """
		return self._dirty_heading

	@property
	def is_dirty_body(self):
		u""" Return True if the heading's body is marked dirty """
		return self._dirty_body

	def get_index_in_parent_list(self):
		""" Retrieve the index value of current heading in the parents list of
		headings. This works also for top level headings.

		:returns:	Index value or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			if self in self.parent.children:
				return self.parent.children.index(self)
		elif self.document:
			if self in self.document.headings:
				return self.document.headings.index(self)

	def get_parent_list(self):
		""" Retrieve the parents list of headings. This works also for top
		level headings.

		:returns:	List of headings or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			if self in self.parent.children:
				return self.parent.children
		elif self.document:
			if self in self.document.headings:
				return self.document.headings

	def set_dirty(self):
		u""" Mark the heading and body dirty so that it will be rewritten when
		saving the document """
		self._dirty_heading = True
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_heading(self):
		u""" Mark the heading dirty so that it will be rewritten when saving the
		document """
		self._dirty_heading = True
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_body(self):
		u""" Mark the heading's body dirty so that it will be rewritten when
		saving the document """
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	@property
	def document(self):
		u""" Read only access to the document. If you want to change the
		document, just assign the heading to another document """
		return self._document

	@property
	def parent(self):
		u""" Access to the parent heading """
		return self._parent

	@property
	def number_of_parents(self):
		u""" Access to the number of parent headings before reaching the root
		document """
		def count_parents(h):
			if h.parent:
				return 1 + count_parents(h.parent)
			else:
				return 0
		return count_parents(self)

	@property
	def previous_sibling(self):
		u""" Access to the previous heading that's a sibling of the current one
		"""
		return self._previous_sibling

	@property
	def next_sibling(self):
		u""" Access to the next heading that's a sibling of the current one """
		return self._next_sibling

	@property
	def previous_heading(self):
		u""" Serialized access to the previous heading """
		if self.previous_sibling:
			h = self.previous_sibling
			while h.children:
				h = h.children[-1]
			return h
		elif self.parent:
			return self.parent

	@property
	def next_heading(self):
		u""" Serialized access to the next heading """
		if self.children:
			return self.children[0]
		elif self.next_sibling:
			return self.next_sibling
		else:
			h = self.parent
			while h:
				if h.next_sibling:
					return h.next_sibling
				else:
					h = h.parent

	@property
	def start(self):
		u""" Access to the starting line of the heading """
		if self.document is None:
			return self._orig_start

		# static computation of start
		if not self.document.is_dirty:
			return self._orig_start

		# dynamic computation of start, really slow!
		def compute_start(h):
			if h:
				return len(h) + compute_start(h.previous_heading)
			return len(self.document.meta_information) if \
					self.document.meta_information else 0
		return compute_start(self.previous_heading)

	@property
	def start_vim(self):
		if self.start is not None:
			return self.start + 1

	@property
	def end(self):
		u""" Access to the ending line of the heading """
		if self.start is not None:
			return self.start + len(self.body)

	@property
	def end_vim(self):
		if self.end is not None:
			return self.end + 1

	@property
	def end_of_last_child(self):
		u""" Access to end of the last child """
		if self.children:
			child = self.children[-1]
			while child.children:
				child = child.children[-1]
			return child.end
		return self.end

	@property
	def end_of_last_child_vim(self):
		return self.end_of_last_child + 1

	def children():
		u""" Subheadings of the current heading """
		def fget(self):
			return self._children

		def fset(self, value):
			v = value
			if type(v) in (list, tuple) or isinstance(v, UserList):
				v = flatten_list(v)
			self._children[:] = v

		def fdel(self):
			del self.children[:]

		return locals()
	children = property(**children())

	@property
	def first_child(self):
		u""" Access to the first child heading or None if no children exist """
		if self.children:
			return self.children[0]

	@property
	def last_child(self):
		u""" Access to the last child heading or None if no children exist """
		if self.children:
			return self.children[-1]

	def level():
		u""" Access to the heading level """
		def fget(self):
			return self._level

		def fset(self, value):
			self._level = int(value)
			self.set_dirty_heading()

		def fdel(self):
			self.level = None

		return locals()
	level = property(**level())

	def todo():
		u""" Todo state of current heading. When todo state is set, it will be
		converted to uppercase """
		def fget(self):
			# extract todo state from heading
			return self._todo

		def fset(self, value):
			# update todo state
			if type(value) not in (unicode, str, type(None)):
				raise ValueError(u'Todo state must be a string or None.')
			if value and not REGEX_TODO.match(value):
				raise ValueError(u'Found non allowed character in todo state! %s' % value)
			if not value:
				self._todo = None
			else:
				v = value
				if type(v) == str:
					v = v.decode(u'utf-8')
				self._todo = v.upper()
			self.set_dirty_heading()

		def fdel(self):
			self.todo = None

		return locals()
	todo = property(**todo())

	def active_date():
		u"""
		active date of the hearing.

		active dates are used in the agenda view. they can be part of the
		heading and/or the body.
		"""
		def fget(self):
			return self._active_date

		def fset(self, value):
			self._active_date = value

		def fdel(self):
			self._active_date = None
		return locals()
	active_date = property(**active_date())

	def title():
		u""" Title of current heading """
		def fget(self):
			return self._title.strip()

		def fset(self, value):
			if type(value) not in (unicode, str):
				raise ValueError(u'Title must be a string.')
			v = value
			if type(v) == str:
				v = v.decode(u'utf-8')
			self._title = v.strip()
			self.set_dirty_heading()

		def fdel(self):
			self.title = u''

		return locals()
	title = property(**title())

	def tags():
		u""" Tags of the current heading """
		def fget(self):
			return self._tags

		def fset(self, value):
			v = value
			if type(v) in (unicode, str):
				v = list(unicode(v))
			if type(v) not in (list, tuple) and not isinstance(v, UserList):
				v = list(unicode(v))
			v = flatten_list(v)
			v_decoded = []
			for i in v:
				if type(i) not in (unicode, str):
					raise ValueError(u'Found non string value in tags! %s' % unicode(i))
				if u':' in i:
					raise ValueError(u'Found non allowed character in tag! %s' % i)
				i_tmp = i.strip().replace(' ', '_').replace('\t', '_')
				if type(i) == str:
					i_tmp = i.decode(u'utf-8')
				v_decoded.append(i_tmp)

			self._tags[:] = v_decoded

		def fdel(self):
			self.tags = []

		return locals()
	tags = property(**tags())

	def body():
		u""" Holds the content belonging to the heading """
		def fget(self):
			return self._body

		def fset(self, value):
			if type(value) in (list, tuple) or isinstance(value, UserList):
				self._body[:] = flatten_list(value)
			elif type(value) in (str, ):
				self._body[:] = value.decode('utf-8').split(u'\n')
			elif type(value) in (unicode, ):
				self._body[:] = value.split(u'\n')
			else:
				self.body = list(unicode(value))

		def fdel(self):
			self.body = []

		return locals()
	body = property(**body())


class HeadingList(MultiPurposeList):
	u"""
	A Heading List just contains headings. It's used for documents to store top
	level headings and for headings to store subheadings.

	A Heading List must be linked to a Document or Heading!

	See documenatation of MultiPurposeList for more information.
	"""
	def __init__(self, initlist=None, obj=None):
		"""
		:initlist:	Initial data
		:obj:		Link to a concrete Heading or Document object
		"""
		# it's not necessary to register a on_change hook because the heading
		# list will itself take care of marking headings dirty or adding
		# headings to the deleted headings list
		MultiPurposeList.__init__(self)

		self._obj = obj

		# initialization must be done here, because
		# self._document is not initialized when the
		# constructor of MultiPurposeList is called
		if initlist:
			self.extend(initlist)

	@classmethod
	def is_heading(cls, obj):
		return isinstance(obj, Heading)

	def _get_document(self):
		if self.__class__.is_heading(self._obj):
			return self._obj._document
		return self._obj

	def _add_to_deleted_headings(self, item):
		u"""
		Serialize headings so that all subheadings are also marked for deletion
		"""
		if not self._get_document():
			# HeadingList has not yet been associated
			return

		if type(item) in (list, tuple) or isinstance(item, UserList):
			for i in flatten_list(item):
				self._add_to_deleted_headings(i)
		else:
			self._get_document()._deleted_headings.append(
					item.copy(including_children=False))
			self._add_to_deleted_headings(item.children)
			self._get_document().set_dirty_document()

	def _associate_heading(self, heading, previous_sibling, next_sibling,
			children=False):
		"""
		:heading:		The heading or list to associate with the current heading
		:previous_sibling:	The previous sibling of the current heading. If
							heading is a list the first heading will be
							connected with the previous sibling and the last
							heading with the next sibling. The items in between
							will be linked with one another.
		:next_sibling:	The next sibling of the current heading. If
							heading is a list the first heading will be
							connected with the previous sibling and the last
							heading with the next sibling. The items in between
							will be linked with one another.
		:children:	Marks whether children are processed in the current
					iteration or not (should not be use, it's set automatically)
		"""
		# TODO this method should be externalized and moved to the Heading class
		if type(heading) in (list, tuple) or isinstance(heading, UserList):
			prev = previous_sibling
			current = None
			for _next in flatten_list(heading):
				if current:
					self._associate_heading(current, prev, _next, children=children)
					prev = current
				current = _next
			if current:
				self._associate_heading(current, prev, next_sibling, children=children)
		else:
			heading._orig_start = None
			heading._orig_len = None
			d = self._get_document()
			if heading._document != d:
				heading._document = d
			if not children:
				# connect heading with previous and next headings
				heading._previous_sibling = previous_sibling
				if previous_sibling:
					previous_sibling._next_sibling = heading
				heading._next_sibling = next_sibling
				if next_sibling:
					next_sibling._previous_sibling = heading

				if d == self._obj:
					# self._obj is a Document
					heading._parent = None
				elif heading._parent != self._obj:
					# self._obj is a Heading
					heading._parent = self._obj
			heading.set_dirty()

			self._associate_heading(heading.children, None, None, children=True)

	def __setitem__(self, i, item):
		if not self.__class__.is_heading(item):
			raise ValueError(u'Item is not a heading!')
		if item in self:
			raise ValueError(u'Heading is already part of this list!')
		self._add_to_deleted_headings(self[i])

		self._associate_heading(item, \
				self[i - 1] if i - 1 >= 0 else None, \
				self[i + 1] if i + 1 < len(self) else None)
		MultiPurposeList.__setitem__(self, i, item)

	def __setslice__(self, i, j, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		o = flatten_list(o)
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		i = max(i, 0)
		j = max(j, 0)
		self._add_to_deleted_headings(self[i:j])
		self._associate_heading(o, \
				self[i - 1] if i - 1 >= 0 and i < len(self) else None, \
				self[j] if j >= 0 and j < len(self) else None)
		MultiPurposeList.__setslice__(self, i, j, o)

	def __delitem__(self, i):
		item = self[i]
		if item.previous_sibling:
			item.previous_sibling._next_sibling = item.next_sibling
		if item.next_sibling:
			item.next_sibling._previous_sibling = item.previous_sibling

		self._add_to_deleted_headings(item)
		MultiPurposeList.__delitem__(self, i)

	def __delslice__(self, i, j):
		i = max(i, 0)
		j = max(j, 0)
		items = self[i:j]
		if items:
			first = items[0]
			last = items[-1]
			if first.previous_sibling:
				first.previous_sibling._next_sibling = last.next_sibling
			if last.next_sibling:
				last.next_sibling._previous_sibling = first.previous_sibling
		self._add_to_deleted_headings(items)
		MultiPurposeList.__delslice__(self, i, j)

	def __iadd__(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in flatten_list(o):
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		self._associate_heading(o, self[-1] if len(self) > 0 else None, None)
		return MultiPurposeList.__iadd__(self, o)

	def __imul__(self, n):
		# TODO das müsste eigentlich ein klonen von objekten zur Folge haben
		return MultiPurposeList.__imul__(self, n)

	def append(self, item):
		if not self.__class__.is_heading(item):
			raise ValueError(u'Item is not a heading!')
		if item in self:
			raise ValueError(u'Heading is already part of this list!')
		self._associate_heading(item, self[-1] if len(self) > 0 else None, None)
		MultiPurposeList.append(self, item)

	def insert(self, i, item):
		self._associate_heading(item, \
				self[i - 1] if i - 1 >= 0 and i - 1 < len(self) else None,
				self[i] if i >= 0 and i < len(self) else None)
		MultiPurposeList.insert(self, i, item)

	def pop(self, i=-1):
		item = self[i]
		self._add_to_deleted_headings(item)
		del self[i]
		return item

	def remove(self, item):
		self.__delitem__(self.index(item))

	def reverse(self):
		MultiPurposeList.reverse(self)
		prev_h = None
		for h in self:
			h._previous_sibling = prev_h
			h._next_sibling = None
			prev_h._next_sibling = h
			h.set_dirty()
			prev_h = h

	def sort(self, *args, **kwds):
		MultiPurposeList.sort(*args, **kwds)
		prev_h = None
		for h in self:
			h._previous_sibling = prev_h
			h._next_sibling = None
			prev_h._next_sibling = h
			h.set_dirty()
			prev_h = h

	def extend(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		self._associate_heading(o, self[-1] if len(self) > 0 else None, None)
		MultiPurposeList.extend(self, o)


# vim: set noexpandtab:
ftplugin/orgmode/liborgmode/__init__.py	[[[1
1
# -*- coding: utf-8 -*-
ftplugin/orgmode/liborgmode/base.py	[[[1
120
# -*- coding: utf-8 -*-

"""
	base
	~~~~~~~~~~

	Here are some really basic data structures that are used throughout
	the liborgmode.
"""

from UserList import UserList


def flatten_list(l):
	"""TODO"""
	res = []
	if type(l) in (tuple, list) or isinstance(l, UserList):
		for i in l:
			if type(i) in (list, tuple) or isinstance(i, UserList):
				res.extend(flatten_list(i))
			else:
				res.append(i)
	return res


class Direction():
	u"""
	Direction is used to indicate the direction of certain actions.

	Example: it defines the direction headings get parted in.
	"""
	FORWARD = 1
	BACKWARD = 2


class MultiPurposeList(UserList):
	u"""
	A Multi Purpose List is a list that calls a user defined hook on
	change. The implementation is very basic - the hook is called without any
	parameters. Otherwise the Multi Purpose List can be used like any other
	list.

	The member element "data" can be used to fill the list without causing the
	list to be marked dirty. This should only be used during initialization!
	"""

	def __init__(self, initlist=None, on_change=None):
		UserList.__init__(self, initlist)
		self._on_change = on_change

	def _changed(self):
		u"""
		Call hook
		"""
		if callable(self._on_change):
			self._on_change()

	def __setitem__(self, i, item):
		UserList.__setitem__(self, i, item)
		self._changed()

	def __delitem__(self, i):
		UserList.__delitem__(self, i)
		self._changed()

	def __setslice__(self, i, j, other):
		UserList.__setslice__(self, i, j, other)
		self._changed()

	def __delslice__(self, i, j):
		UserList.__delslice__(self, i, j)
		self._changed()

	def __getslice__(self, i, j):
		# fix UserList - don't return a new list of the same type but just the
		# normal list item
		i = max(i, 0)
		j = max(j, 0)
		return self.data[i:j]

	def __iadd__(self, other):
		res = UserList.__iadd__(self, other)
		self._changed()
		return res

	def __imul__(self, n):
		res = UserList.__imul__(self, n)
		self._changed()
		return res

	def append(self, item):
		UserList.append(self, item)
		self._changed()

	def insert(self, i, item):
		UserList.insert(self, i, item)
		self._changed()

	def pop(self, i=-1):
		item = self[i]
		del self[i]
		return item

	def remove(self, item):
		self.__delitem__(self.index(item))

	def reverse(self):
		UserList.reverse(self)
		self._changed()

	def sort(self, *args, **kwds):
		UserList.sort(self, *args, **kwds)
		self._changed()

	def extend(self, other):
		UserList.extend(self, other)
		self._changed()


# vim: set noexpandtab:
ftplugin/orgmode/liborgmode/agenda.py	[[[1
60
# -*- coding: utf-8 -*-

u"""
    Agenda
    ~~~~~~~~~~~~~~~~~~

    The agenda is one of the main concepts of orgmode.
    TODO

	* filtering
	* sorting
"""

from orgmode.liborgmode.agendafilter import *


class AgendaManager(object):
	u"""Simple parsing of Documents to create an agenda."""

	def __init__(self):
		super(AgendaManager, self).__init__()

	def get_todo(self, documents):
		u"""
		Get the todo agenda for the given documents (list of document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(), [contains_active_todo])
			filtered.extend(tmp)
		return sorted(filtered)

	def get_next_week_and_active_todo(self, documents):
		u"""
		Get the agenda for next week for the given documents (list of
		document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(),
				[is_within_week_and_active_todo])
			filtered.extend(tmp)
		return sorted(filtered)

	def get_timestamped_items(self, documents):
		u"""
		Get all time-stamped items in a time-sorted way for the given
		documents (list of document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(),
				[contains_active_date])
			filtered.extend(tmp)
		return sorted(filtered)

# vim: set noexpandtab:
ftplugin/orgmode/settings.py	[[[1
83
# -*- coding: utf-8 -*-

import vim

SCOPE_ALL = 1

# for all vim-orgmode buffers
SCOPE_GLOBAL = 2

# just for the current buffer - has priority before the global settings
SCOPE_BUFFER = 4

VARIABLE_LEADER = {SCOPE_GLOBAL: u'g', SCOPE_BUFFER: u'b'}

u""" Evaluate and store settings """

def get(setting, default=None, scope=SCOPE_ALL):
	u""" Evaluate setting in scope of the current buffer,
	globally and also from the contents of the current buffer

	WARNING: Only string values are converted to unicode. If a different value
	is received, e.g. a list or dict, no conversion is done.

	:setting: name of the variable to evaluate
	:default: default value in case the variable is empty

	:returns: variable value
	"""
	# TODO first read setting from org file which take precedence over vim
	# variable settings
	if scope & SCOPE_ALL | SCOPE_BUFFER and int(vim.eval((u'exists("b:%s")' % setting).encode(u'utf-8'))):
		res = vim.eval((u"b:%s" % setting).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res

	elif scope & SCOPE_ALL | SCOPE_GLOBAL and int(vim.eval((u'exists("g:%s")' % setting).encode(u'utf-8'))):
		res = vim.eval((u"g:%s" % setting).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res
	return default

def set(setting, value, scope=SCOPE_GLOBAL, overwrite=False):
	u""" Store setting in the definied scope

	WARNING: For the return value, only string are converted to unicode. If a
	different value is received by vim.eval, e.g. a list or dict, no conversion
	is done.

	:setting: name of the setting
	:value: the actual value, repr is called on the value to create a string representation
	:scope: the scope o the setting/variable
	:overwrite: overwrite existing settings (probably user definied settings)

	:returns: the new value in case of overwrite==False the current value
	"""
	if not overwrite and int(vim.eval((u'exists("%s:%s")' % (VARIABLE_LEADER[scope], setting)).encode(u'utf-8'))):
		res = vim.eval((u'%s:%s' % (VARIABLE_LEADER[scope], setting)).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res
	v = repr(value)
	if type(value) == unicode:
		# strip leading u of unicode string representations
		v = v[1:]

	vim.command((u'let %s:%s = %s' % (VARIABLE_LEADER[scope], setting, v)).encode(u'utf-8'))
	return value

def unset(setting, scope=SCOPE_GLOBAL):
	u""" Unset setting int the definied scope
	:setting: name of the setting
	:scope: the scope o the setting/variable

	:returns: last value of setting
	"""
	value = get(setting, scope=scope)
	vim.command((u'unlet! %s:%s' % (VARIABLE_LEADER[scope], setting)).encode(u'utf-8'))
	return value


# vim: set noexpandtab:
ftplugin/orgmode/exceptions.py	[[[1
19
# -*- coding: utf-8 -*-

class PluginError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class BufferNotFound(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class BufferNotInSync(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class HeadingDomError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

# vim: set noexpandtab:
ftplugin/orgmode/vimbuffer.py	[[[1
452
# -*- coding: utf-8 -*-

"""
	vimbuffer
	~~~~~~~~~~

	VimBuffer and VimBufferContent are the interface between liborgmode and
	vim.

	VimBuffer extends the liborgmode.document.Document().
	Document() is just a general implementation for loading an org file. It
	has no interface to an actual file or vim buffer. This is the task of
	vimbuffer.VimBuffer(). It is the interfaces to vim. The main tasks for
	VimBuffer are to provide read and write access to a real vim buffer.

	VimBufferContent is a helper class for VimBuffer. Basically, it hides the
	details of encoding - everything read from or written to VimBufferContent
	is UTF-8.
"""

from UserList import UserList

import vim

import settings
from exceptions import BufferNotFound, BufferNotInSync
from liborgmode.documents import Document, MultiPurposeList, Direction
from liborgmode.headings import Heading


class VimBuffer(Document):
	def __init__(self, bufnr=0):
		u"""
		:bufnr:		0: current buffer, every other number refers to another buffer
		"""
		Document.__init__(self)
		self._bufnr            = vim.current.buffer.number if bufnr == 0 else bufnr
		self._changedtick      = -1
		self._cached_heading   = None

		if self._bufnr == vim.current.buffer.number:
			self._content = VimBufferContent(vim.current.buffer)
		else:
			_buffer = None
			for b in vim.buffers:
				if self._bufnr == b.number:
					_buffer = b
					break

			if not _buffer:
				raise BufferNotFound(u'Unable to locate buffer number #%d' % self._bufnr)
			self._content = VimBufferContent(_buffer)

		self.update_changedtick()
		self._orig_changedtick = self._changedtick

	@property
	def tabstop(self):
		return int(vim.eval(u'&ts'.encode(u'utf-8')))

	@property
	def tag_column(self):
		return int(settings.get('org_tag_column', '77'))

	@property
	def is_insync(self):
		if self._changedtick == self._orig_changedtick:
			self.update_changedtick()
		return self._changedtick == self._orig_changedtick

	@property
	def bufnr(self):
		u"""
		:returns:	The buffer's number for the current document
		"""
		return self._bufnr

	def changedtick():
		""" Number of changes in vimbuffer """
		def fget(self):
			return self._changedtick
		def fset(self, value):
			self._changedtick = value
		return locals()
	changedtick = property(**changedtick())

	def get_todo_states(self, strip_access_key=True):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		:returns:	[([todo states], [done states]), ..]
		"""
		states = settings.get(u'org_todo_keywords', [])
		if type(states) not in (list, tuple):
			return []

		def parse_states(s, stop=0):
			res = []
			if not s:
				return res
			if type(s[0]) in (unicode, str):
				r = []
				for i in s:
					_i = i
					if type(_i) == str:
						_i = _i.decode(u'utf-8')
					if type(_i) == unicode and _i:
						if strip_access_key and u'(' in _i:
							_i = _i[:_i.index(u'(')]
							if _i:
								r.append(_i)
						else:
							r.append(_i)
				if not u'|' in r:
					if not stop:
						res.append((r[:-1], [r[-1]]))
					else:
						res = (r[:-1], [r[-1]])
				else:
					seperator_pos = r.index(u'|')
					if not stop:
						res.append((r[0:seperator_pos], r[seperator_pos + 1:]))
					else:
						res = (r[0:seperator_pos], r[seperator_pos + 1:])
			elif type(s) in (list, tuple) and not stop:
				for i in s:
					r = parse_states(i, stop=1)
					if r:
						res.append(r)
			return res

		return parse_states(states)

	def update_changedtick(self):
		if self.bufnr == vim.current.buffer.number:
			self._changedtick = int(vim.eval(u'b:changedtick'.encode(u'utf-8')))
		else:
			vim.command(u'unlet! g:org_changedtick | let g:org_lz = &lz | let g:org_hidden = &hidden | set lz hidden'.encode(u'utf-8'))
			# TODO is this likely to fail? maybe some error hangling should be added
			vim.command((u'keepalt buffer %d | let g:org_changedtick = b:changedtick | buffer %d' % \
					(self.bufnr, vim.current.buffer.number)).encode(u'utf-8'))
			vim.command(u'let &lz = g:org_lz | let &hidden = g:org_hidden | unlet! g:org_lz g:org_hidden | redraw'.encode(u'utf-8'))
			self._changedtick = int(vim.eval(u'g:org_changedtick'.encode(u'utf-8')))

	def write(self):
		u""" write the changes to the vim buffer

		:returns:	True if something was written, otherwise False
		"""
		if not self.is_dirty:
			return False

		self.update_changedtick()
		if not self.is_insync:
			raise BufferNotInSync(u'Buffer is not in sync with vim!')

		# write meta information
		if self.is_dirty_meta_information:
			meta_end = 0 if self._orig_meta_information_len is None else self._orig_meta_information_len
			self._content[:meta_end] = self.meta_information
			self._orig_meta_information_len = len(self.meta_information)

		# remove deleted headings
		already_deleted = []
		for h in sorted(self._deleted_headings, cmp=lambda x, y: cmp(x._orig_start, y._orig_start), reverse=True):
			if h._orig_start is not None and h._orig_start not in already_deleted:
				# this is a heading that actually exists on the buffer and it
				# needs to be removed
				del self._content[h._orig_start:h._orig_start + h._orig_len]
				already_deleted.append(h._orig_start)
		del self._deleted_headings[:]
		del already_deleted

		# update changed headings and add new headings
		for h in self.all_headings():
			if h.is_dirty:
				if h._orig_start is not None:
					# this is a heading that existed before and was changed. It
					# needs to be replaced
					if h.is_dirty_heading:
						self._content[h.start:h.start + 1] = [unicode(h)]
					if h.is_dirty_body:
						self._content[h.start + 1:h.start + h._orig_len] = h.body
				else:
					# this is a new heading. It needs to be inserted
					self._content[h.start:h.start] = [unicode(h)] + h.body
				h._dirty_heading = False
				h._dirty_body = False
			# for all headings the length and start offset needs to be updated
			h._orig_start = h.start
			h._orig_len = len(h)

		self._dirty_meta_information = False
		self._dirty_document = False

		self.update_changedtick()
		self._orig_changedtick = self._changedtick
		return True

	def write_heading(self, heading, including_children=True):
		""" WARNING: use this function only when you know what you are doing!
		This function writes a heading to the vim buffer. It offers performance
		advantages over the regular write() function. This advantage is
		combined with no sanity checks! Whenever you use this function, make
		sure the heading you are writing contains the right offsets
		(Heading._orig_start, Heading._orig_len).

		Usage example:
			# Retrieve a potentially dirty document
			d = ORGMODE.get_document(allow_dirty=True)
			# Don't rely on the DOM, retrieve the heading afresh
			h = d.find_heading(direction=Direction.FORWARD, position=100)
			# Update tags
			h.tags = ['tag1', 'tag2']
			# Write the heading
			d.write_heading(h)

		This function can't be used to delete a heading!

		:heading:				Write this heading with to the vim buffer
		:including_children:	Also include children in the update

		:returns				The written heading
		"""
		if including_children and heading.children:
			for child in heading.children[::-1]:
				self.write_heading(child, including_children)

		if heading.is_dirty:
			if heading._orig_start is not None:
				# this is a heading that existed before and was changed. It
				# needs to be replaced
				if heading.is_dirty_heading:
					self._content[heading._orig_start:heading._orig_start + 1] = [unicode(heading)]
				if heading.is_dirty_body:
					self._content[heading._orig_start + 1:heading._orig_start + heading._orig_len] = heading.body
			else:
				# this is a new heading. It needs to be inserted
				raise ValueError('Heading must contain the attribute _orig_start! %s' % heading)
			heading._dirty_heading = False
			heading._dirty_body = False
		# for all headings the length offset needs to be updated
		heading._orig_len = len(heading)

		return heading

	def previous_heading(self, position=None):
		u""" Find the next heading (search forward) and return the related object
		:returns:	Heading object or None
		"""
		h = self.current_heading(position=position)
		if h:
			return h.previous_heading

	def current_heading(self, position=None):
		u""" Find the current heading (search backward) and return the related object
		:returns:	Heading object or None
		"""
		if position is None:
			position = vim.current.window.cursor[0] - 1

		if not self.headings:
			return

		def binaryFindInDocument():
			hi = len(self.headings)
			lo = 0
			while lo < hi:
				mid = (lo+hi)//2
				h = self.headings[mid]
				if h.end_of_last_child < position:
					lo = mid + 1
				elif h.start > position:
					hi = mid
				else:
					return binaryFindHeading(h)

		def binaryFindHeading(heading):
			if not heading.children or heading.end >= position:
				return heading

			hi = len(heading.children)
			lo = 0
			while lo < hi:
				mid = (lo+hi)//2
				h = heading.children[mid]
				if h.end_of_last_child < position:
					lo = mid + 1
				elif h.start > position:
					hi = mid
				else:
					return binaryFindHeading(h)

		# look at the cache to find the heading
		h_tmp = self._cached_heading
		if h_tmp is not None:
			if h_tmp.end_of_last_child > position and \
					h_tmp.start < position:
				if h_tmp.end < position:
					self._cached_heading = binaryFindHeading(h_tmp)
				return self._cached_heading

		self._cached_heading = binaryFindInDocument()
		return self._cached_heading

	def next_heading(self, position=None):
		u""" Find the next heading (search forward) and return the related object
		:returns:	Heading object or None
		"""
		h = self.current_heading(position=position)
		if h:
			return h.next_heading

	def find_current_heading(self, position=None, heading=Heading):
		u""" Find the next heading backwards from the position of the cursor.
		The difference to the function current_heading is that the returned
		object is not built into the DOM. In case the DOM doesn't exist or is
		out of sync this function is much faster in fetching the current
		heading.

		:position:	The position to start the search from

		:heading:	The base class for the returned heading

		:returns:	Heading object or None
		"""
		return self.find_heading(vim.current.window.cursor[0] - 1 \
				if position is None else position, \
				direction=Direction.BACKWARD, heading=heading, \
				connect_with_document=False)


class VimBufferContent(MultiPurposeList):
	u""" Vim Buffer Content is a UTF-8 wrapper around a vim buffer. When
	retrieving or setting items in the buffer an automatic conversion is
	performed.

	This ensures UTF-8 usage on the side of liborgmode and the vim plugin
	vim-orgmode.
	"""

	def __init__(self, vimbuffer, on_change=None):
		MultiPurposeList.__init__(self, on_change=on_change)

		# replace data with vimbuffer to make operations change the actual
		# buffer
		self.data = vimbuffer

	def __contains__(self, item):
		i = item
		if type(i) is unicode:
			i = item.encode(u'utf-8')
		return MultiPurposeList.__contains__(self, i)

	def __getitem__(self, i):
		item = MultiPurposeList.__getitem__(self, i)
		if type(item) is str:
			return item.decode(u'utf-8')
		return item

	def __getslice__(self, i, j):
		return [item.decode(u'utf-8') if type(item) is str else item \
				for item in MultiPurposeList.__getslice__(self, i, j)]

	def __setitem__(self, i, item):
		_i = item
		if type(_i) is unicode:
			_i = item.encode(u'utf-8')

		MultiPurposeList.__setitem__(self, i, _i)

	def __setslice__(self, i, j, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
			o_tmp = list(o_tmp)
		for item in o_tmp:
			if type(item) == unicode:
				o.append(item.encode(u'utf-8'))
			else:
				o.append(item)
		MultiPurposeList.__setslice__(self, i, j, o)

	def __add__(self, other):
		raise NotImplementedError()
		# TODO: implement me
		if isinstance(other, UserList):
			return self.__class__(self.data + other.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(self.data + other)
		else:
			return self.__class__(self.data + list(other))

	def __radd__(self, other):
		raise NotImplementedError()
		# TODO: implement me
		if isinstance(other, UserList):
			return self.__class__(other.data + self.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(other + self.data)
		else:
			return self.__class__(list(other) + self.data)

	def __iadd__(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) is unicode:
				o.append(i.encode(u'utf-8'))
			else:
				o.append(i)

		return MultiPurposeList.__iadd__(self, o)

	def append(self, item):
		i = item
		if type(item) is str:
			i = item.encode(u'utf-8')
		MultiPurposeList.append(self, i)

	def insert(self, i, item):
		_i = item
		if type(_i) is str:
			_i = item.encode(u'utf-8')
		MultiPurposeList.insert(self, i, _i)

	def index(self, item, *args):
		i = item
		if type(i) is unicode:
			i = item.encode(u'utf-8')
		MultiPurposeList.index(self, i, *args)

	def pop(self, i=-1):
		return MultiPurposeList.pop(self, i).decode(u'utf-8')

	def extend(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) is unicode:
				o.append(i.encode(u'utf-8'))
			else:
				o.append(i)
		MultiPurposeList.extend(self, o)


# vim: set noexpandtab:
ftplugin/org.vim	[[[1
104
" org.vim -- Text outlining and task management for Vim based on Emacs' Org-Mode
" @Author       : Jan Christoph Ebersbach (jceb@e-jc.de)
" @License      : AGPL3 (see http://www.gnu.org/licenses/agpl.txt)
" @Created      : 2010-10-03
" @Last Modified: Tue 13. Sep 2011 20:52:57 +0200 CEST
" @Revision     : 0.4
" @vi           : ft=vim:tw=80:sw=4:ts=4

if ! has('python') || v:version < 703
	echoerr "Unable to start orgmode. Orgmode depends on Vim >= 7.3 with Python support complied in."
	finish
endif

if ! exists("b:did_ftplugin")
	" default emacs settings
	setlocal comments-=s1:/*,mb:*,ex:*/ conceallevel=2 concealcursor=nc tabstop=8 shiftwidth=8 commentstring=#\ %s

	" register keybindings if they don't have been registered before
	if exists("g:loaded_org")
		python ORGMODE.register_keybindings()
	endif
endif

" load plugin just once
if &cp || exists("g:loaded_org")
    finish
endif
let g:loaded_org = 1

" general setting plugins that should be loaded and their order
if ! exists('g:org_plugins') && ! exists('b:org_plugins')
	let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Hyperlinks', '|', 'Todo', 'TagsProperties', 'Date', 'Agenda', 'Misc', '|', 'Export']
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

function! <SID>OrgDeleteUnusedDocument(bufnr)
python << EOF
b = int(vim.eval('a:bufnr'))
if b in ORGMODE._documents:
	del ORGMODE._documents[b]
EOF
endfunction

" show and hide Org menu depending on the filetype
augroup orgmode
	au BufEnter		*		:if &filetype == "org" | call <SID>OrgRegisterMenu() | endif
	au BufLeave		*		:if &filetype == "org" | call <SID>OrgUnregisterMenu() | endif
	au BufDelete	*		:call <SID>OrgDeleteUnusedDocument(expand('<abuf>'))
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

" ******************** Taglist/Tagbar integration ********************

" tag-bar support for org-mode
let g:tagbar_type_org = {
			\ 'ctagstype' : 'org',
			\ 'kinds'     : [
				\ 's:sections',
				\ 'h:hyperlinks',
			\ ],
			\ 'sort'    : 0,
			\ 'deffile' : expand('<sfile>:p:h') . '/org.cnf'
			\ }

" taglist support for org-mode
if !exists('g:Tlist_Ctags_Cmd')
	finish
endif

" Pass parameters to taglist
let g:tlist_org_settings = 'org;s:section;h:hyperlinks'
let g:Tlist_Ctags_Cmd .= ' --options=' . expand('<sfile>:p:h') . '/org.cnf '
doc/orgguide.txt	[[[1
1371
*orgguide.txt*          For Vim version 7.3       Last change: 2011 September 27

     _  _  ____  __  __    _____  ____   ___  __  __  _____  ____  ____
    ( \/ )(_  _)(  \/  )  (  _  )(  _ \ / __)(  \/  )(  _  )(  _ \( ___)
     \  /  _)(_  )    (    )(_)(  )   /( (_-. )    (  )(_)(  )(_) ))__)
      \/  (____)(_/\/\_)  (_____)(_)\_) \___/(_/\/\_)(_____)(____/(____)


==============================================================================
TABLE OF CONTENTS                            *org* *org-toc* *orgguide* *orgguide-toc*

    1.  About vim-orgmode guide          |orgguide-about|
    2.  Introduction                     |orgguide-introduction|
    3.  Document structure               |orgguide-docstructure|
    4.  Tables                           |orgguide-tables|
    5.  Hyperlinks                       |orgguide-hyperlinks|
    6.  Todo items                       |orgguide-todo|
    7.  Tags                             |orgguide-tags|
    8.  Properties                       |orgguide-properties|
    9.  Dates and Times                  |orgguide-dates|
    10. Capture - Refile - Archive       |orgguide-capture|
    11. Agenda views                     |orgguide-agenda|
    12. Export/Markup for rich export    |orgguide-export|
    13. Publishing                       |orgguide-publishing|
    14. Working with source code         |orgguide-source|
    15. Miscellaneous                    |orgguide-misc|
    16. MobileOrg                        |orgguide-mobileorg|
    17. Customization                    |orgguide-customization|
    18. Development                      |orgguide-development|
    19. License vim-orgmode              |orgguide-license|
    20. Contributors                     |orgguide-contributors|
    21. Changelog                        |orgguide-changelog|
    22. Links                            |orgguide-links|
    23. Development                      |orgguide-development|

==============================================================================
ORG MODE GUIDE                                                  *orgguide-about*

Copyright © 2010 Free Software Foundation

  Permission is granted to copy, distribute and/or modify this document under
  the terms of the GNU Free Documentation License, Version 1.3 or any later
  version published by the Free Software Foundation; with no Invariant
  Sections, with the Front-Cover texts being “A GNU Manual,” and with the
  Back-Cover Texts as in (a) below. A copy of the license is included in the
  section entitled “GNU Free Documentation License.”

  (a) The FSF’s Back-Cover Text is: “You have the freedom to copy and modify
  this GNU manual. Buying copies from the FSF supports it in developing GNU
  and promoting software freedom.”

  This document is part of a collection distributed under the GNU Free
  Documentation License. If you want to distribute this document separately
  from the collection, you can do so by adding a copy of the license to the
  document, as described in section 6 of the license.

==============================================================================
INTRODUCTION                                 *vim-orgmode* *orgguide-introduction*

Vim-orgmode: Text outlining and task management for Vim based on Emacs'
Org-Mode.

The idea for this plugin was born by listening to the Floss Weekly podcast
introducing Emacs' Org-Mode (http://twit.tv/floss136). Org-Mode has a lot of
strong features like folding, views (sparse tree) and scheduling of tasks.
These are completed by hyperlinks, tags, todo states, priorities aso.

Vim-orgmode aims at providing the same functionality for Vim and for command
line tools*.

* for command line tools and other programs a library liborgmode is provided.
  It encapsulates all functionality for parsing and modifying org files.

------------------------------------------------------------------------------
Preface~
   vim-orgmode is a file type plugin for keeping notes, maintaining TODO
   lists, and doing project planning with a fast and effective plain-text
   system. It is also an authoring and publishing system.

   This document is a copy of the orgmode-guide for emacs
   (http://orgmode.org/) with modifications for vim. It contains all basic
   features and commands, along with important hints for customization.

------------------------------------------------------------------------------
Features~
  vim-orgmode is still very young but already quite usable. Here is a short
  list of the already supported features:

  - Cycle visibility of headings
  - Navigate between headings
  - Edit the structure of the document: add, move, promote, denote headings
    and more
  - Hyperlinks within vim-orgmode and outside (files, webpages, etc.)
  - TODO list management
  - Tags for headings
  - Basic date handling
  - Export (via emacs)

  More features are coming...

------------------------------------------------------------------------------
Default mappings~
                                                                  *org-mappings*
Here is a short overview of the default mappings. They also can be invoked
via the 'Org' menu. Most are only usable in command mode.
 
  Show/Hide:~
    <TAB>           - Cycle Visibility

  Editing Structure:~
    <C-S-CR>        - Heading above
    <S-CR>          - Heading below
    <C-CR>          - Heading above, after children

    m]]             - move subtree down
    m[[             - move subtree up

    yah             - yank heading 
    dah             - delete heading 
    yat             - yank subtree
    dat             - delete subtree
    p               - paste subtree
    
    >> or >ah       - promote heading
    << or <ah       - demote heading
    >at             - promote subtree
    <at             - demote subtree

  Hyperlinks:~
    gl              - goto link
    gyl             - yank link
    gil             - insert new link

    gn              - next link
    go              - previous link

  TODO Lists:~
    ,d              - select keyword
    <S-Left>        - previous keyword
    <S-Right>       - next keyword
    <C-S-Left>      - previous keyword set
    <C-S-Right>     - next keyword set

  TAGS and properties:~
    <localleader>t      - set tags
    
  Dates:~
    <localleader>sa     - insert date
    <localleader>sai    - insert inactive date

  Agenda:~
    <localleader>caa    - agenda for the week
    <localleader>cat    - agenda of all TODOs
    <localleader>caT    - timeline for current buffer

  Export:~
    <localleader>ep     - export as PDF
    <localleader>eh     - export as HTML

------------------------------------------------------------------------------
Installation~
  Download latest stable release at
  http://www.vim.org/scripts/script.php?script_id=3642

  Open the vimball archive in vim and source it.

  $ vim orgmode.vbm
>
    :so %
<

  ATTENTION: All .pyc files of former versions of vim-orgmode need to be
  deleted beforehand!

------------------------------------------------------------------------------
Activation~
  Add the following line to your .vimrc file to ensure that filetype plugins
  are loaded properly:
>
  filetype plugin indent on
<

  Please install the Universal Text Linking
  (http://www.vim.org/scripts/script.php?script_id=293) addon, otherwise
  hyperlinks won't work. Other plugins that integrate well with vim orgmode
  are listed in the following section.

------------------------------------------------------------------------------
Suggested plugins~
  Universal Text Linking~
    (http://www.vim.org/scripts/script.php?script_id=293) general support for
    text linking. The hyperlinks feature of vim-orgmode depends on this plugin.

  repeat~
    (http://www.vim.org/scripts/script.php?script_id=2136)
    Repeat actions that would not be repeatable otherwise. This plugin is
    needed when you want to repeat the previous orgmode action.

  taglist~
    ([http://www.vim.org/scripts/script.php?script_id=273)
    Display tags for the currently edited file. Vim-orgmode ships with support
    for displaying the heading structure and hyperlinks in the taglist plugin.

  tagbar~
    (http://www.vim.org/scripts/script.php?script_id=3465)
    A new approach to displaying tags for the currently edited file.
    Vim-orgmode ships with support for displaying the heading structure and
    hyperlinks in the tagbar plugin.

  speeddating~
    (http://www.vim.org/scripts/script.php?script_id=2120)
    In-/decrease dates the vim way: C-a and C-x. Dates and times in the
    orgmode format can be in-/decreased if this plugins is installed.

  Narrow Region~
    (http://www.vim.org/scripts/script.php?script_id=3075)
    Emulation of Emacs' Narrow Region feature. It might be useful when dealing
    with large orgmode files.

  pathogen~
    (http://www.vim.org/scripts/script.php?script_id=2332)
    Easy management of multiple vim plugins.

------------------------------------------------------------------------------
Feedback~
   If you find problems with vim-orgmode, or if you have questions, remarks, or
   ideas about it, please create a ticket on
   https://github.com/jceb/vim-orgmode

==============================================================================
DOCUMENT STRUCTURE                                       *orgguide-docstructure*

------------------------------------------------------------------------------
Outlines~
  Outlines allow a document to be organized in a hierarchical structure, which
  (at least for me) is the best representation of notes and thoughts. An
  overview of this structure is achieved by folding (hiding) large parts of
  the document to show only the general document structure and the parts
  currently being worked on. vim-orgmode greatly simplifies the use of
  outlines by compressing the entire show/hide functionality into a single
  command, <Plug>OrgToggleFolding, which is bound to the <TAB> key.

------------------------------------------------------------------------------
Headlines~
  Headlines define the structure of an outline tree. The headlines in
  vim-orgmode start with one or more stars, on the left margin. For example:
>
  * Top level headline
  ** Second level
  *** 3rd level
      some text
  *** 3rd level
      more text

  * Another top level headline
<

  Some people find the many stars too noisy and would prefer an outline
  that has whitespace followed by a single star as headline starters.
  |g:org_heading_shade_leading_stars| describes a setup to realize this.

------------------------------------------------------------------------------
Text objects~
  Vim offers a mighty feature called |text-objects|. A text object is bound to
  a certain character sequence that can be used in combination with all kinds
  of editing and selection tasks.

  vim-orgmode implements a number of text objects to make editing org files
  easier:

  ih                    inner heading, referring to the current heading
                        excluding the heading level characters (*)
  ah                    a heading, referring to the current heading including
                        everything
  it                    inner subtree, starting with the current heading
  at                    a subtree, starting with the current heading
  Oh                    inner outer heading, referring to the parent
  Ot                    inner outer heading, including subtree, referring to
                        the parent
  OH                    a outer heading
  OT                    a outer subtree

  Motions can be used like text objects as well. See |orgguide-motion|.

------------------------------------------------------------------------------
Visibility cycling~
  Outlines make it possible to hide parts of the text in the buffer.
  vim-orgmode uses just two commands, bound to <Tab> and <S-Tab> to change the
  visibility in the buffer.

  <Tab>       or                                *orgguide-Tab* or *orgguide-S-Tab*
  <S-Tab>               Subtree cycling: Rotate current subtree among the
                        states
>
  ,-> FOLDED -> CHILDREN -> SUBTREE --.
  '-----------------------------------'
<

  When called with the shift key, global cycling is invoked.

  <LocalLeader>,    or      *orgguide-<LocalLeader>,* or *orgguide-<LocalLeader>.*
  <LocalLeader>.        Global cycling: Rotate the entire buffer among the
                        states. The same can be achieved by using the
                        keybindings zm and zr.
>
  ,-> OVERVIEW -> CONTENTS -> SHOW ALL --.
  '--------------------------------------'
<

  Vim-orgmode doesn't implement the following functionality, yet.~
  When Emacs first visits an org file, the global state is set to
  OVERVIEW, i.e. only the top level headlines are visible. This can be
  configured through the variable =org-startup-folded=, or on a per-file
  basis by adding a startup keyword =overview=, =content=, =showall=, like
  this:
>
   #+STARTUP: content
<
------------------------------------------------------------------------------
Motion~
                                                               *orgguide-motion*
  The following commands jump to other headlines in the buffer.

  }                     Next heading.

  {                     Previous heading.

  ]]                    Next heading same level.

  [[                    Previous heading same level.

  g{                    Backward to higher level heading.

  g}                    Forward to higher level heading.

------------------------------------------------------------------------------
Structure editing~

                                                                 *orgguide-S-CR*
  <S-CR>                Insert new heading with same level as current. If the
                        cursor is in a plain list item, a new item is created
                        (see section [[#Plain-lists][Plain lists]]). When this
                        command is used in the middle of a line, the line is
                        split and the rest of the line becomes the new
                        headline.

  Not yet implemented in vim-orgmode~
  M-S-<CR>              Insert new TODO entry with same level as current
                        heading.

  <Tab>         or
  <S-Tab>               In a new entry with no text yet, <Tab> and <S-Tab>
                        will cycle through reasonable levels.

  <<            or                              *orgguide-<<* or *orgguide-CTRL-d*
  <C-d> (insert mode)   Promote current heading by one level.

  >>            or                              *orgguide->>* or *orgguide-CTRL-t*
  <C-t> (insert mode)   Demote current heading by one level.

                                                                  *orgguide-<[[*
  <[[                   Promote the current subtree by one level.

                                                                  *orgguide->]]*
  >]]                   Demote the current subtree by one level.

                                                                  *orgguide-m[[*
  m[[                   Move subtree up/down (swap with previous/next subtree
                        of same level).

                                                                  *orgguide-m]]*
  m]]                   Move subtree up/down (swap with previous/next subtree
                        of same level).

  Not yet implemented in vim-orgmode~
  C-c C-w                Refile entry or region to a different location. See
                        section [[#Refiling-notes][Refiling notes]].

                                                           *orgguide-<Leader>nr*
  <Leader>nr            Narrow buffer to current subtree / widen it again
                        (only if NarrowRegion plugin is installed)

  When there is an active region (Transient Mark mode), promotion and demotion
  work on all headlines in the region.

------------------------------------------------------------------------------
Sparse trees~
    Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Plain lists~
  Within an entry of the outline tree, hand-formatted lists can provide
  additional structure.

  Not yet implemented in vim-orgmode~
  They also provide a way to create lists of checkboxes (see section
  |orgguide-checkboxes|).

  vim-orgmode supports editing such lists, and the HTML exporter (see section
  |orgguide-export|) parses and formats them.

  vim-orgmode knows ordered lists, unordered lists, and description lists.

  -  'Unordered' list items start with ‘-’, ‘+’, or ‘*’ as bullets.
  -  'Ordered' list items start with ‘1.’ or ‘1)’.
  -  'Description' list use ‘ :: ’ to separate the 'term' from the
     description.

  Items belonging to the same list must have the same indentation on the
  first line. An item ends before the next line that is indented like its
  bullet/number, or less. A list ends when all items are closed, or before
  two blank lines. An example:
>
  ** Lord of the Rings
     My favorite scenes are (in this order)
     1. The attack of the Rohirrim
     2. Eowyn's fight with the witch king
        + this was already my favorite scene in the book
        + I really like Miranda Otto.
     Important actors in this film are:
     - Elijah Wood :: He plays Frodo
     - Sean Austin :: He plays Sam, Frodo's friend.
<

  The following commands act on items when the cursor is in the first line
  of an item (the line with the bullet or number).

  Not yet implemented in vim-orgmode~
  The following commands act on items when the cursor is in the first line of
  an item (the line with the bullet or number).

------------------------------------------------------------------------------
Footnotes~
  Not yet implemented in vim-orgmode~

==============================================================================
TABLES                                                         *orgguide-tables*
  Not yet implemented in vim-orgmode~

==============================================================================
HYPERLINKS                                                 *orgguide-hyperlinks*

NOTE: The |utl| plugin is used for this feature and needs to be installed.
      http://www.vim.org/scripts/script.php?script_id=293

Like HTML, vim-orgmode provides links inside a file, external links to other
files, Usenet articles, emails, and much more.

------------------------------------------------------------------------------
Link format~
                                                           *orgguide-linkformat*
  vim-orgmode will recognize plain URL-like links and activate them as links.
  The general link format, however, looks like this:
>
    [[link][description]]       or alternatively           [[link]]
<

  Once a link in the buffer is complete (all brackets present), and you are
  not in insert mode, or you are editing another line, vim-orgmode will change
  the display so that 'description' is displayed instead of
  '[[link][description]]' and 'link' is displayed instead of '[[link]]'.  To
  edit the invisible ‘link’ part, go into insert mode, or call the
  'Insert/edit Link' command by pressing 'gil'.

------------------------------------------------------------------------------
Internal links~
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
External links~
  |utl| supports links to files and websites. Others can be added by extending
  utl (see |utl-smartSamples|).  External links are URL-like locators. They
  start with a short identifying string followed by a colon. There can be no
  space after the colon. Here are some examples:
>
    http://www.astro.uva.nl/~dominik          on the web
    file:/home/dominik/images/jupiter.jpg     file, absolute path
    /home/dominik/images/jupiter.jpg          same as above
<

  A link should be enclosed in double brackets and may contain a descriptive
  text to be displayed instead of the URL (see section |orgguide-linkformat|),
  for example:
>
    [[http://www.vim.org/][VIM]]
<

------------------------------------------------------------------------------
Handling links~
  vim-orgmode provides methods to create a link in the correct syntax, to
  insert it into an org file, and to follow the link.

  Not yet implemented in vim-orgmode~
  C-c l                 Store a link to the current location. This is a
                        /global/ command (you must create the key binding
                        yourself) which can be used in any buffer to create a
                        link. The link will be stored for later insertion into
                        an org buffer (see below).

                                                                  *orgguide-gil*
  gil                   Insert a link. This prompts for a link to be inserted
                        into the buffer. You can just type a link, or use
                        history keys <Up> and <Down> to access stored links.
                        You will be prompted for the description part of the
                        link. File name completion is enabled to link to a
                        local file. In addition vim-orgmode provides the
                        command :OrgHyperlinkInsert to insert a link from
                        command line.

  gil                   When the cursor is on an existing link, gil allows you
                        to edit the link and description parts of the link.

  Not yet implemented in vim-orgmode~
  C-c C-o or mouse-1 or mouse-2  Open link at point.

  Not yet implemented in vim-orgmode~
  C-c &                 Jump back to a recorded position. A position is
                        recorded by the commands following internal links, and
                        by C-c %. Using this command several times in direct
                        succession moves through a ring of previously recorded
                        positions.

------------------------------------------------------------------------------
Targeted links~
  Not yet implemented in vim-orgmode~

==============================================================================
TODO ITEMS                                                       *orgguide-todo*

vim-orgmode does not maintain TODO lists as separate documents. Instead,
TODO items are an integral part of the notes file, because TODO items usually
come up while taking notes! With vim-orgmode, simply mark any entry in a tree as
being a TODO item. In this way, information is not duplicated, and the entire
context from which the TODO item emerged is always present.

Of course, this technique for managing TODO items scatters them throughout
your notes file. vim-orgmode compensates for this by providing methods to give
you an overview of all the things that you have to do.

------------------------------------------------------------------------------
Using TODO states~

  Any headline becomes a TODO item when it starts with the word ‘TODO’,
  for example:
>
      *** TODO Write letter to Sam Fortune
<

  The most important commands to work with TODO entries are:

  <LocalLeader>t        Rotate the TODO state of the current item among. See
                        |orgguide-tags-settings|for more information.
>
       ,-> (unmarked) -> TODO -> DONE --.
       '--------------------------------'
<

  Not yet implemented in vim-orgmode~
  The same rotation can also be done “remotely” from the timeline and
  agenda buffers with the t command key (see section
  |orgguide-agenda-commands|).

  <S-right> or <S-left> Select the following/preceding TODO state, similar to
                        cycling.

  Not yet implemented in vim-orgmode~
  C-c / t               View TODO items in a /sparse tree/ (see section
                        [[#Sparse-trees][Sparse trees]]). Folds the buffer,
                        but shows all TODO items and the headings hierarchy
                        above them.

  <LocalLeader>cat      Show the global TODO list. This collects the TODO
                        items from all agenda files (see section
                        |orgguide-agenda-views|) into a single buffer.

  Not yet implemented in vim-orgmode~
  S-M-<CR>              Insert a new TODO entry below the current one.

------------------------------------------------------------------------------
Multi-state workflows~

  You can use TODO keywords to indicate different 'sequential' states in
  the process of working on an item, for example:
>
  :let g:org_todo_keywords=['TODO', 'FEEDBACK', 'VERIFY', '|', 'DONE', 'DELEGATED']
<

  The vertical bar separates the TODO keywords (states that 'need action')
  from the DONE states (which need 'no further action'). If you don’t
  provide the separator bar, the last state is used as the DONE state.
  With this setup, the command <S-Right> will cycle an entry from TODO to
  FEEDBACK, then to VERIFY, and finally to DONE and DELEGATED.

  Sometimes you may want to use different sets of TODO keywords in
  parallel. For example, you may want to have the basic TODO/DONE, but
  also a workflow for bug fixing, and a separate state indicating that an
  item has been canceled (so it is not DONE, but also does not require
  action). Your setup would then look like this:
>
  :let g:org_todo_keywords = [['TODO(t)', '|', 'DONE(d)'],
      \ ['REPORT(r)', 'BUG(b)', 'KNOWNCAUSE(k)', '|', 'FIXED(f)'],
      \ ['CANCELED(c)']]
<
  The keywords should all be different, this helps vim-orgmode to keep track
  of which subsequence should be used for a given entry. The example also
  shows how to define keys for fast access of a particular state, by
  adding a letter in parenthesis after each keyword - you will be prompted
  for the key after pressing ,d.

                                                       *orgguide-<LocalLeader>d*
  <LocalLeader>d        prompt for fast access of a todo state

  Not yet implemented in vim-orgmode~
  To define TODO keywords that are valid only in a single file, use the
  following text anywhere in the file.

>
  #+BEGIN_EXAMPLE
      #+TODO: TODO(t) | DONE(d)
      #+TODO: REPORT(r) BUG(b) KNOWNCAUSE(k) | FIXED(f)
      #+TODO: | CANCELED(c)
  #+END_EXAMPLE
<

  After changing one of these lines, use C-c C-c with the cursor still in
  the line to make the changes known to vim-orgmode.

------------------------------------------------------------------------------
Progress logging~
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Priorities~
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Breaking tasks down into subtasks~
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Checkboxes~
                                                           *orgguide-checkboxes*
  Not yet implemented in vim-orgmode~

==============================================================================
TAGS                                                             *orgguide-tags*

An excellent way to implement labels and contexts for cross-correlating
information is to assign 'tags' to headlines. vim-orgmode has extensive
support for tags.

Every headline can contain a list of tags; they occur at the end of the
headline. Tags are normal words containing letters, numbers, ‘_’, and
‘@’. Tags must be preceded and followed by a single colon, e.g.,
‘:work:’. Several tags can be specified, as in ‘:work:urgent:’. Tags
will by default be in bold face with the same color as the headline.

------------------------------------------------------------------------------
Tag inheritance~
                                                     *orgguide-tags-inheritance*
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Setting tags~
                                                        *orgguide-tags-settings*
  Tags can simply be typed into the buffer at the end of a headline. After
  a colon, <TAB> offers completion on tags. There is also a special
  command for inserting tags:

                                                       *orgguide-<LocalLeader>t*
  <LocalLeader>t        Enter new tags for the current headline. vim-orgmode
                        will either offer completion or a special single-key
                        interface for setting tags, see below.  After pressing
                        <CR>, the tags will be inserted and aligned to
                        'org-tags-column'.

  vim-orgmode will support tag insertion based on a 'list of tags'. By default
  this list is constructed dynamically, containing all tags currently used
  in the buffer.

------------------------------------------------------------------------------
Tag searches~
                                                          *orgguide-tags-search*
  Not yet implemented in vim-orgmode~

==============================================================================
PROPERTIES                                                 *orgguide-properties*

  Not yet implemented in vim-orgmode~

==============================================================================
DATES AND TIMES                                                 *orgguide-dates*

To assist project planning, TODO items can be labeled with a date and/or
a time. The specially formatted string carrying the date and time
information is called a 'timestamp' in vim-orgmode.

------------------------------------------------------------------------------
Timestamps~

  A timestamp is a specification of a date (possibly with a time or a range of
  times) in a special format, either <2003-09-16 Tue> or <2003-09-16 Tue
  09:39> or <2003-09-16 Tue 12:00-12:30>. A timestamp can appear anywhere in
  the headline or body of an org tree entry.  Its presence causes entries to
  be shown on specific dates in the agenda (see section |orgguide-agenda|). We
  distinguish:

  Plain timestamp; Event; Appointment ~
    A simple timestamp just assigns a date/time to an item. This is just like
    writing down an appointment or event in a paper agenda.
>
    * Meet Peter at the movies <2006-11-01 Wed 19:15>
    * Discussion on climate change <2006-11-02 Thu 20:00-22:00>
<
  Timestamp with repeater interval ~
    Not yet implemented in vim-orgmode~

  Diary-style sexp entries ~
    Not yet implemented in vim-orgmode~

  Time/Date range~
    Two timestamps connected by ‘--’ denote a range.
>
    ** Meeting in Amsterdam
       <2004-08-23 Mon>--<2004-08-26 Thu>
<
  Inactive timestamp~
    Just like a plain timestamp, but with square brackets instead of angular
    ones. These timestamps are inactive in the sense that they do 'not'
    trigger an entry to show up in the agenda.
>
    * Gillian comes late for the fifth time [2006-11-01 Wed]
<
------------------------------------------------------------------------------
Creating timestamps~

  For vim-orgmode to recognize timestamps, they need to be in the specific
  format. All commands listed below produce timestamps in the correct format.

                                                      *orgmode-<LocalLeader>-sa*
  <LocalLeader>sa       Prompt for a date and insert a corresponding timestamp.

                        Not yet implemented in vim-orgmode~
                        When the cursor is at an existing timestamp in the
                        buffer, the command is used to modify this timestamp
                        instead of inserting a new one.

                        Not yet implemented in vim-orgmode~
                        When this command is used twice in succession, a time
                        range is inserted. With a prefix, also add the current
                        time.

                                                       *orgmode-<LocalLeader>si*
  <LocalLeader>si       Like |orgmode-<LocalLeader>-sa|, but insert an inactive
                        timestamp that will not cause an agenda entry.

                                              *orgmode-ctrl-a* or *orgmode-ctrl-x*
  CTRL-A or CTRL-X      Change the item under the cursor in a timestamp.
                        The cursor can be on a year, month, day, hour or
                        minute.  NOTE: The plugin 'speeddating' should be
                        installed for this feature.

                        Not yet implemented in vim-orgmode~
                        When the timestamp contains a time range like
                        ‘15:30-16:30’, modifying the first time will also
                        shift the second, shifting the time block with
                        constant length.  To change the length, modify the
                        second time.

  When vim-orgmode prompts for a date/time, it will accept any string
  containing some date and/or time information, and intelligently interpret
  the string, deriving defaults for unspecified information from the current
  date and time. See the manual for more information on how exactly the
  date/time prompt works.

  Not yet implemented in vim-orgmode~
  You can also select a date in the pop-up calendar.

------------------------------------------------------------------------------
Deadlines and scheduling~
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Clocking work time~
  Not yet implemented in vim-orgmode~

==============================================================================
CAPTURE - REFILE - ARCHIVE                                    *orgguide-capture*

  Not yet implemented in vim-orgmode~

==============================================================================
AGENDA VIEWS                                                   *orgguide-agenda*

Due to the way vim-orgmode works, TODO items, time-stamped items, and tagged
headlines can be scattered throughout a file or even a number of files. To get
an overview of open action items, or of events that are important for a
particular date, this information must be collected, sorted and displayed in
an organized way. There are several different views, see below.

The extracted information is displayed in a special agenda buffer. This
buffer is read-only.

Not yet implemented in vim-orgmode~
... but provides commands to visit the corresponding locations in the original
org files, and even to edit these files remotely.  Remote editing from the
agenda buffer means, for example, that you can change the dates of deadlines
and appointments from the agenda buffer. The commands available in the Agenda
buffer are listed in |orgguide-agenda-commands|.

- |orgguide-agenda-files|          Files being searched for agenda information
- |orgguide-agenda-dispatcher|     Keyboard access to agenda views
- |orgguide-agenda-views|          What is available out of the box?
- |orgguide-agenda-commands|       Remote editing of org trees
- |orgguide-agenda-custom|         Defining special searches and views

------------------------------------------------------------------------------
Agenda files~
                                                         *orgguide-agenda-files*
  The information to be shown is normally collected from all 'agendafiles',
  the files listed in the variable *g:org_agenda_files* .

  You can change the list of agenda files like this:
>
    let g:org_agenda_files = ['~/org/index.org', ~/org/project.org']
<
------------------------------------------------------------------------------
The agenda dispatcher ~
                                                    *orgguide-agenda-dispatcher*
  Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
The built-in agenda views ~
                                                         *orgguide-agenda-views*

  The weekly/daily agenda~
    The purpose of the weekly/daily 'agenda' is to act like a page of a
    paper agenda, showing all the tasks for the current week or day.

                                                     *orgguide-<LocalLeader>caa*
    <LocalLeader>caa    Compile an agenda for the current week from a list of
                        org files. The agenda shows the entries for each day.

  The global TODO list~
    The global TODO list contains all unfinished TODO items formatted and
    collected into a single place.

    Not yet implemented in vim-orgmode~
    Remote editing of TODO items lets you change the state of a TODO entry
    with a single key press. The commands available in the TODO list are
    described in |agenda-commands|

                                                     *orgguide-<LocalLeader>cat*
    <LocalLeader>cat    Show the global TODO list. This collects the TODO
                        items from all agenda files into a single buffer.

    Not yet implemented in vim-orgmode~
                                                     *orgguide-<LocalLeader>caT*
    <LocalLeader>caT    Like the above, but allows selection of a specific
                        TODO keyword.

  Matching tags and properties~
    Not yet implemented in vim-orgmode~

  Timeline for a single file~
    The timeline summarizes all time-stamped items from a single vim-orgmode
    file in a /time-sorted view/. The main purpose of this command is to
    give an overview over events in a project.

                                                     *orgguide-<LocalLeader>caL*
    <LocalLeader>caL    Show a time-sorted view of the vim-orgmode, with all
                        time-stamped items.

  Search view~
    Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Commands in the agenda buffer~
                                                      *orgguide-agenda-commands*
  Entries in the agenda buffer are linked back to the org file where they
  originate. Commands are provided to show and jump to the
  original entry location, and to edit the org files “remotely” from the
  agenda buffer.

  Not yet implemented in vim-orgmode~
  only partly implemented

  Motion~
    Not yet implemented in vim-orgmode~

  View/Go to org file~
                                                           *orgguide-agenda-Tab*
    <Tab>               Go to the original location of the idem in an
                        alternative window.

                                                            *orgguide-agenda-CR*
    <CR>                Go to the original location of the item and stay in
                        the same/the agenda window.

                                                          *orgguide-agenda-S-CR*
    <S-CR>              Go to the original location of the item in a new split
                        window.

    Not yet implemented in vim-orgmode~

  Change display~
    Not yet implemented in vim-orgmode~

------------------------------------------------------------------------------
Custom agenda views~
                                                        *orgguide-agenda-custom*
  Not yet implemented in vim-orgmode~

==============================================================================
EXPORTING                                                      *orgguide-export*

NOTE: vim-orgmode relies on emacs and orgmode for emacs for this feature.
      Both need to be installed.

vim-orgmode documents can be exported into a variety of other formats:
ASCII export for inclusion into emails, HTML to publish on the web,
LaTeX/PDF for beautiful printed documents and DocBook to enter the world
of many other formats using DocBook tools. There is also export to
iCalendar format so that planning information can be incorporated into
desktop calendars.

Simply use the 'export' menu.

==============================================================================
PUBLISHING                                                 *orgguide-publishing*

  Not yet implemented in vim-orgmode~

==============================================================================
WORKING WITH SOURCE CODE                                       *orgguide-source*

  Not yet implemented in vim-orgmode~

==============================================================================
MISCELLANEOUS                                                    *orgguide-misc*

  Not yet implemented in vim-orgmode~

==============================================================================
MOBILEORG                                                   *orgguide-mobileorg*

  Not yet implemented in vim-orgmode~

==============================================================================
CUSTOMIZATION                                           *orgguide-customization*

------------------------------------------------------------------------------
Remapping shortcuts~
  vim-orgmode provides an easy way for remapping the default keyboard
  shortcuts. For this task it relies on vim's <Plug> mappings. All shortcuts
  of vim-orgmode are accessible by <Plug>s.

  To change a keyboard shortcut the name of the related <Plug> is needed.
  First we need to look up the current mapping in the Org menu. The following
  command reveals the <Plug>'s name:
>
  :map <current_mapping>
<

  The result should look something like this:
>
  :map ,t
  n ,t @<Plug>OrgSetTags
<

  Now we can create an alternate mapping:
>
  nmap <new_mapping> <the_plug>
<

  To change the mapping for editing tags to <leader>t the vimrc entry would
  look like this:
>
  nmap <leader>t @<Plug>OrgSetTags
<

------------------------------------------------------------------------------
Syntax highlighting~
  Syntax highlighting is customizable to fit nicely with the user's
  colorscheme.

                                                *g:org_heading_highlight_colors*
  Define the highlighting colors/group names for headings (default):
>
  let g:org_heading_highlight_colors = ['Title', 'Constant', 'Identifier',
    \   'Statement', 'PreProc', 'Type', 'Special']
<

                                                *g:org_heading_highlight_levels*
  Definie the number of levels of highlighting. If this number is bigger than
  the list of colors defined in of g:org_heading_highlight_colors the colors
  of g:org_heading_highlight_colors get repeated (default):
>
  let g:org_heading_highlight_levels = len(g:org_heading_highlight_colors)
<

                                             *g:org_heading_shade_leading_stars*
  Defines if leading stars are displayed in the color of the heading or if a
  special NonText highlighting is used that hides them from user (default):
>
  let g:org_heading_shade_leading_stars = 1
<

                                                           *g:org_todo_keywords*
  Defines the keywords that are highlighted in headings. For more information
  about this variable, please consult the org-mode documentation
  (http://orgmode.org/org.html#index-org_002dtodo_002dkeywords-511) (default):
>
  let g:org_todo_keywords = ['TODO', '|', 'DONE']
<

                                                      *g:org_todo_keyword_faces*
  Defines special faces (styles) for displaying g:org_todo_keywords. Please
  refer to vim documentation (topic |attr-list|) for allowed values for
  :weight, :slant, :decoration. Muliple colors can be separated by comma for
  :foreground and :background faces to provide different colors for gui and
  terminal mode (default):
>
  let g:org_todo_keyword_faces = []
<

  Syntax Highlighting Examples~
    Define an additionaly keyword 'WAITING' and set the foreground color to
    'cyan'. Define another keyword 'CANCELED' and set the foreground color to
    red, background to black and the weight to normal, slant to italc and
    decoration to underline:

>
    let g:org_todo_keywords = [['TODO', 'WAITING', '|', 'DONE'],
      \   ['|', 'CANCELED']]
    let g:org_todo_keyword_faces = [['WAITING', 'cyan'], ['CANCELED',
      \   [':foreground red', ':background black', ':weight bold',
      \   ':slant italic', ':decoration underline']]]
<
==============================================================================
DEVELOPMENT                                               *orgguide-development*

The development of vim-orgmode is coordinated via github:
  https://github.com/jceb/vim-orgmode

If you like this project, have questions, suggestions or problems, simply drop
us a line and open an issue. Patches are very welcome!

Here is a quick start about the vim-orgmode development.

------------------------------------------------------------------------------
Structure and Source Code~
  The majority of the source code is stored in folder ftplugin/orgmode. This
  is where the actual functionality of the plugin is located.

  I choose to implement vim-orgmode mainly in Python. I hope this will ease
  the implementation especially with the functionality of the Python standard
  library at hand.

  Right below the directory ftplugin/orgmode the basic implementation of
  vim-orgmode is found. This basic functionality provides everything for
  higher level implementations that modify the buffer, provide a menu and
  keybindings to the user and everything else that is needed.

  Below the directory ftplugin/orgmode/plugins the plugins are located. Every
  plugin must provide a class equal to its filename with the .py-extension.
  An example for a plugin can be found in file
  ftplugin/orgmode/plugins/Example.py.

  Every plugin must be enabled by the user by setting the g:org_plugins
  variable. By default all shipped plugins are enabled.  Example:
>
    let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure']
<

  Files and folders~
    .
    ├── debian                  - files needed for building a Debian package
    ├── doc                     - vim documentation
    ├── documentation           - development documentation
    ├── examples                - example of aplugin
    ├── ftdetect                - Filetype detection for orgmode files
    ├── ftplugin                - Home of the main part of vim-orgmode
    │   └── orgmode             - Home for all Python code
    │       ├── liborgmode      - vim unrelated part of vim-orgmde. Contains
    │       │                     basic data structures and algorithms to
    │       │                     parse and edit orgfiles.
    │       └── plugins         - Home for all orgmode plugins
    ├── indent                  - Indentation for orgmode files
    ├── syntax                  - Syntax highlighting
    ├── tests                   - Tests to verify the consistency and
    │                             correctness of orgmode and the plugins
    ├── build_vmb.vim           - Build file for creating a Vimball
    ├── install-vbm.vim         - Local installation of vbm via make target
    ├── LICENSE                 - License Information
    ├── README.org              - README :)
    └── Makefile                - make commands

------------------------------------------------------------------------------
Writing a plugin~
  To write a plugin:
  1. copy file ftplugin/orgmode/plugins/Example.py to
     ftplugin/orgmode/plugins/YourPlugin.py
  2. Change class name to "YourPlugin"
  3. Set the menu name, it doesn't need to match the filename anymore, e.g.
     "Your Plugin"
  4. Prepare keybindings in function register by defining a proper action and
     a key this action should be mapped to. For further information refer to
     section Keybindings.
  5. Register your plugin:
>
  let g:org_plugins = ['ShowHide', '|', 'Navigator', 'EditStructure',
    \ 'YourPlugin']
<

  6. Write unittests and implement YourPlugin.

------------------------------------------------------------------------------
Keybindings~
  Keybindings alias mappings are described very well in the vim
  documentation, see |map-modes|. vim-orgmode tries to make it easy for the
  developer to register new keybindings, make them customizable and provide
  menu entries so that the user can access the functionality like in original
  orgmode.

  This is done by providing three classes: Keybinding, Plug and ActionEntry

  Keybinding~
    This is the basic class that encapsulates a single keybinding consisting
    of a key/mapping and an action. Several options can be set when creating
    the object to specify the mode and all kinds of other things.

    If a Plug is given instead of an action string the Plug is bound to the
    key. All relevant data is read from the Plug, e.g. name, mode aso.

    Example~
      Map g{ to moving to parent heading in normal mode:
>
      Keybinding('g{', \
        ':py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>', \
        mode=MODE_NORMAL)

      vim -> :nmap g{
        \ :py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>
<

      Map g{ to moving to parent heading in normal mode by using a Plug:
>
      Keybinding('g{', Plug('OrgJumpToParentNormal', \
        ':py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>'))

      vim -> :nnoremap <Plug>OrgJumpToParentNormal :py
        \ ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>
      vim -> :nmap g{ <Plug>OrgJumpToParentNormal
<

  Plug~
    A Plug is a unique keybinding that can not be executed by pressing
    any key. This makes it a special Keybinding that takes a name and
    an action to create an object. A plug normally goes together with a
    regular Keybinding to bind the Plug to a key.

    This special behavior is needed to ensure that keybindings are
    customizable by the user. If the user creates a keybinding to a
    Plug the Keybinding object makes sure that the users keybinding is
    used and the keybinding specified by the plugin is not used.

    Example~
      Map g{ to moving to parent heading in normal mode by using a Plug:
>
      Keybinding('g{', Plug('OrgJumpToParentNormal', \
        ':py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>'))

      vim -> :nnoremap <Plug>OrgJumpToParentNormal
        \ :py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>
      vim -> :nmap g{ <Plug>OrgJumpToParentNormal
<

  ActionEntry~
    An ActionEntry makes Keybindings accessible by the vim menu. It takes a
    description and a Keybinding object and builds a menu entry from this. The
    resulting object can be added to a Submenu object by using the + operator.

    Example~
      Map g{ to moving to parent heading in normal mode by using a Plug:
>
      k = Keybinding('g{', Plug('OrgJumpToParentNormal', \
        ':py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>'))

      vim -> :nnoremap <Plug>OrgJumpToParentNormal
        \ :py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>
      vim -> :nmap g{ <Plug>OrgJumpToParentNormal

      menu + ActionEntry('&Up', k)
      vim -> :nmenu &Org.&Naviagte Headings.&Up<Tab>g{
        \ <Plug>OrgJumpToParentNormal
>

------------------------------------------------------------------------------
Building a Vimball~
  Vimball is an archive format for vim plugins. It's of use when you want to
  install vim-orgmode for a single user. To build a Vimball just run the
  following command in the root folder of this plugin.  Please make sure that
  vim is installed on your computer:
>
  make vbm
<
  For installing the plugin form the resulting orgmode.vbm.gz file, please
  refer to the Installation section.

------------------------------------------------------------------------------
Building a Debian Package~
   A Debian package is of use when you want to make vim-orgmode available to
   all users on your computer. Make sure you've debhelper and vim installed,
   than run the following command from the root directory of this plugin to
   build the debian package:
>
   dpkg-buildpackage -us -uc
<
   For installing the plugin form the resulting vim-orgmode_X.X.X-X.deb file,
   please refer to the Installation section.

------------------------------------------------------------------------------
Creating Tests Cases~
  For every plugin it's important to write automated test cases. This is
  important to ensure that little changes don't break things at the other end
  of the project.

  vim-orgmode relies on Pyunit (http://docs.python.org/library/unittest.html).
  All tests are located in the tests directory. Run
>
  make test
<

  to run all tests. To create a new test the test should be added to the
  corresponding test file.

  In case a new plugin is created a new test file needs to be created as well.
  The test needs to be added to the test suite located in the file
  tests/run_tests.py.

  Finally the
>
  make coverage
<

  should be run. The result shows the test coverage of all project files. One
  hundred percent (100%) is of course the goal :-)

==============================================================================
LINKS                                                           *orgguide-links*

- Original org-mode for Emacs (http://orgmode.org)

- VimOrganizer, another vim port of Emacs org-mode
  (http://www.vim.org/scripts/script.php?script_id=3342)

==============================================================================
CHANGELOG                                                   *orgguide-changelog*

0.4.0-0
- change heading tree text object to ir/ar... because of vim's it/at text object (closes issue #106)
- improve performance when inserting a new heading below (closes issue #105)
- remove duplicate tags (closes issue #104)
- improve performance in insert mode (closes issue #103)
- improve performance when opening larger org files (closes issue #103)
- replace org.txt by orgguide.txt (closes issue #77)
- change g:org_leader to <LocalLeader> (closes issue #101)
  To restore the previous behavior add the following line to your vimrc:
>
  let maplocalleader = ','
<
- change normal command execution to not remap any key (related to issue #85)
- fix regression timeout when opening folds (closes issue #100)
- vim-orgmode multistate documentation (closes issue #77)
- add support for @-signs in tags (closes issue #98)
- enable file completion for hyperlinks by default (closes issue #97)
- fix traceback when pressing <Esc> while editing a link (closes issue #96)
- implement reverse visibility cycling using <S-Tab> (closes issue #95)
- change ,, and ,. to remap zr and zm. (closes issue #73)
- add .cnf files to the vimball archive (closes #93)
- integrate pylint code checker (closes issue #87)
- solve encoding issues in the agenda plugin (closes issue #86)
- add description for writing test cases
- add coverage report target (closes issue #74)
- add support for plain lists, thanks to Aleksandar Dimitrov (closes issue #81)
- add agenda view, many thanks to Stefan Otte (closes issue #34)
- move cursor to the current todo state when selecting the todo state
  interactively (closes issue #61)
- add parameter scope to method settings.get
- add method settings.unset
- fix cursor positioning when selecting todo states
- improve date plugin
- update vba targets to its new name vmb
- demoting a newly created second level heading doesn't cause all children to
  be deleted anymore (closes issue #65)
- add error message for missing dependencies (closes issue #59)
- rename tests directory
- change licensing of the documentation to GNU Free Documentation License
- integrate orgguide (closes issue #57)
- replace DIRECTION_* with an enum (closes issue #56 and issue #49)

0.3.0-0, 2011-08-09
- fix completion menu popup that disappeared because of the usage of vim.command
  (closes issue #48)
- implement interactive todo state selection (closes issue #5)
- add orgmode group to au commands in TagProperties plugin (closes issue #53)
- allow demotion of first level headings (closes issue #27)
- fix encoding issues in Date plugin
- add general support for multiple todo sequences (closes Issue #46)
- fix folded text for headings containing backslashes or double quotes (closes
  issue #26)
- add Document.get_todo_states() and Document.get_all_todo_states()
- don't confuse upper case words at the beginning of a heading with a todo
    state (closes issue #28)
- fix error in setting tags (issue #25)
- improve split of heading (issue #24)
- add variable g:org_improve_split_heading to enable/disable improve the split
  of headings (issue #24)
- implement shortcut for moving to the partent's next sibling (g}) (issue #22)
- fix duplication of children when inserting a new heading (issue #20)
- always start insert mode when adding a new heading (issue #21)

0.2.1-0, 2011-06-26
- fix encoding of todo states set by the Todo plugin (thanks to Daniel Carl
  and kien for pointing out the issue)
- add documentation for remapping shortcuts
- add documentation for customizing syntax highlighting

0.2.0-0, 2011-06-25
- initial release

==============================================================================
CONTRIBUTORS                                             *orgguide-contributors*

Thanks to all how contributed to vim-orgmode. All contributors are name here
in alphabetic order:

- Stefan Otte
- Aleksandar Dimitrov

==============================================================================
LICENSE VIM-ORGMODE                                           *orgguide-license*

Copyright (C) 2010, 2011 Jan Christoph Ebersbach

http://www.e-jc.de/

All rights reserved.

The source code of this program is made available under the terms of the GNU
Affero General Public License version 3 (GNU AGPL V3) as published by the Free
Software Foundation.

Binary versions of this program provided by Univention to you as well as other
copyrighted, protected or trademarked materials like Logos, graphics, fonts,
specific documentations and configurations, cryptographic keys etc. are
subject to a license agreement between you and Univention and not subject to
the GNU AGPL V3.

In the case you use this program under the terms of the GNU AGPL V3, the
program is provided in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License with
the Debian GNU/Linux or Univention distribution in file
/usr/share/common-licenses/AGPL-3; if not, see <http://www.gnu.org/licenses/>.

vim:tw=78:ts=2:sw=2:expandtab:ft=help:norl:
indent/org.vim	[[[1
110
" Delete the next line to avoid the special indention of items
if !exists("g:org_indent")
  let g:org_indent = 0
endif

setlocal foldtext=GetOrgFoldtext()
setlocal fillchars-=fold:-
setlocal fillchars+=fold:\ 
setlocal foldexpr=GetOrgFolding()
setlocal foldmethod=expr
setlocal indentexpr=GetOrgIndent()
setlocal nolisp
setlocal nosmartindent
setlocal autoindent

function! GetOrgIndent()
python << EOF
from orgmode import indent_orgmode
indent_orgmode()
EOF
	if exists('b:indent_level')
		let l:tmp = b:indent_level
		unlet b:indent_level
		return l:tmp
	else
		return -1
	endif
endfunction

function! GetOrgFolding()
	if mode() == 'i'
		" the cache size is limited to 3, because vim queries the current and
		" both surrounding lines when the user is typing in insert mode. The
		" cache is shared between GetOrgFolding and GetOrgFoldtext
		if ! exists('b:org_folding_cache')
			let b:org_folding_cache = {}
		endif

		if has_key(b:org_folding_cache, v:lnum)
			return b:org_folding_cache[v:lnum][0]
		endif
python << EOF
from orgmode import fold_orgmode
fold_orgmode(allow_dirty=True)
EOF
	else
python << EOF
from orgmode import fold_orgmode
fold_orgmode()
EOF
	endif

	if exists('b:fold_expr')
		let l:tmp = b:fold_expr
		unlet b:fold_expr
		if mode() == 'i'
			if ! has_key(b:org_folding_cache, v:lnum)
				if len(b:org_folding_cache) > 3
					let b:org_folding_cache = {}
				endif
				let b:org_folding_cache[v:lnum] = [l:tmp]
			endif
		endif
		return l:tmp
	else
		return -1
	endif
endfunction

function! SetOrgFoldtext(text)
	let b:foldtext = a:text
endfunction

function! GetOrgFoldtext()
	if mode() == 'i'
		" the cache size is limited to 3, because vim queries the current and
		" both surrounding lines when the user is typing in insert mode. The
		" cache is shared between GetOrgFolding and GetOrgFoldtext
		if ! exists('b:org_folding_cache')
			let b:org_folding_cache = {}
		endif

		if has_key(b:org_folding_cache, v:lnum) &&
					\ len(b:org_folding_cache[v:lnum]) == 2
			return b:org_folding_cache[v:lnum][1]
		endif
python << EOF
from orgmode import fold_text
fold_text(allow_dirty=True)
EOF
	else
python << EOF
from orgmode import fold_text
fold_text()
EOF
	endif

	if exists('b:foldtext')
		let l:tmp = b:foldtext
		unlet b:foldtext
		if mode() == 'i' && has_key(b:org_folding_cache, v:lnum) &&
			if len(b:org_folding_cache[v:lnum]) == 1
				call add(b:org_folding_cache[v:lnum], l:tmp)
			else
				let b:org_folding_cache[v:lnum][2] = l:tmp
			endif
		endif
		return l:tmp
	endif
endfunction
