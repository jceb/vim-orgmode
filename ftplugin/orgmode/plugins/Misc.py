# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_VISUAL, MODE_OPERATOR
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class Misc(object):
	""" Example plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('Misc')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []
	
	def jump_to_first_character(self):
		heading = Heading.current_heading()
		if not heading:
			vim.eval('feedkeys("^", "n")')
			return

		vim.current.window.cursor = (vim.current.window.cursor[0], heading.level + 1)

	def edit_at_first_character(self):
		heading = Heading.current_heading()
		if not heading:
			vim.eval('feedkeys("I", "n")')
			return

		vim.current.window.cursor = (vim.current.window.cursor[0], heading.level + 1)
		vim.command('startinsert')

	#@repeat
	@apply_count
	def i_heading(self, mode='visual', selection='inner', skip_children=False):
		"""
		inner heading text object
		"""
		heading = Heading.current_heading()
		if heading:
			if selection != 'inner':
				heading = heading if not heading.parent else heading.parent

			line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
			line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]

			if mode != 'visual':
				line_start = vim.current.window.cursor[0]
				line_end = line_start

			start = line_start
			end = line_end
			move_one_character_back = '' if mode == 'visual' else 'h'

			if heading.start_vim < line_start:
				start = heading.start_vim
			if heading.end_vim > line_end and not skip_children:
				end = heading.end_vim
			elif heading.end_of_last_child_vim > line_end and skip_children:
				end = heading.end_of_last_child_vim

			if mode != 'visual' and not vim.current.buffer[end - 1]:
				end -= 1
				move_one_character_back = ''

			swap_cursor = 'o' if vim.current.window.cursor[0] == line_start else ''

			if selection == 'inner' and vim.current.window.cursor[0] != line_start:
				h = Heading.find_heading(line_start - 1, DIRECTION_BACKWARD)
				if h:
					heading = h

			visualmode = vim.eval('visualmode()') if mode == 'visual' else 'v'

			if line_start == start and line_start != heading.start_vim:
				if col_start in (0, 1):
					vim.command('normal! %dgg0%s%dgg$%s%s' % (start, visualmode, end, move_one_character_back, swap_cursor))
				else:
					vim.command('normal! %dgg0%dl%s%dgg$%s%s' % (start, col_start - 1, visualmode, end, move_one_character_back, swap_cursor))
			else:
				vim.command('normal! %dgg0%dl%s%dgg$%s%s' % (start, heading.level + 1, visualmode, end, move_one_character_back, swap_cursor))

			if selection == 'inner':
				if mode == 'visual':
					return 'OrgInnerHeadingVisual' if not skip_children else 'OrgInnerTreeVisual'
				else:
					return 'OrgInnerHeadingOperator' if not skip_children else 'OrgInnerTreeOperator'
			else:
				if mode == 'visual':
					return 'OrgOuterHeadingVisual' if not skip_children else 'OrgOuterTreeVisual'
				else:
					return 'OrgOuterHeadingOperator' if not skip_children else 'OrgOuterTreeOperator'
		elif mode == 'visual':
			vim.command('normal! gv')

	#@repeat
	@apply_count
	def a_heading(self, selection='inner', skip_children=False):
		"""
		a heading text object
		"""
		heading = Heading.current_heading()
		if heading:
			if selection != 'inner':
				heading = heading if not heading.parent else heading.parent

			line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
			line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]

			start = line_start
			end = line_end

			if heading.start_vim < line_start:
				start = heading.start_vim
			if heading.end_vim > line_end and not skip_children:
				end = heading.end_vim
			elif heading.end_of_last_child_vim > line_end and skip_children:
				end = heading.end_of_last_child_vim

			swap_cursor = 'o' if vim.current.window.cursor[0] == line_start else ''

			vim.command('normal! %dgg%s%dgg%s' % (start, vim.eval('visualmode()'), end, swap_cursor))
			if selection == 'inner':
				return 'OrgAInnerHeadingVisual' if not skip_children else 'OrgAInnerTreeVisual'
			else:
				return 'OrgAOuterHeadingVisual' if not skip_children else 'OrgAOuterTreeVisual'
		else:
			vim.command('normal! gv')

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding('^', Plug('OrgJumpToFirstCharacter', ':py ORGMODE.plugins["Misc"].jump_to_first_character()<CR>')))
		self.keybindings.append(Keybinding('I', Plug('OrgEditAtFirstCharacter', ':py ORGMODE.plugins["Misc"].edit_at_first_character()<CR>')))

		self.keybindings.append(Keybinding('ih', Plug('OrgInnerHeadingVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].i_heading()<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('ah', Plug('OrgAInnerHeadingVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].a_heading()<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('Oh', Plug('OrgOuterHeadingVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(selection="outer")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('OH', Plug('OrgAOuterHeadingVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].a_heading(selection="outer")<CR>', mode=MODE_VISUAL)))

		self.keybindings.append(Keybinding('ih', Plug('OrgInnerHeadingOperator', ':<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(mode="operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('ah', ':normal Vah<CR>', mode=MODE_OPERATOR))
		self.keybindings.append(Keybinding('Oh', Plug('OrgOuterHeadingOperator', ':<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(mode="operator", selection="outer")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('OH', ':normal VOH<CR>', mode=MODE_OPERATOR))

		self.keybindings.append(Keybinding('it', Plug('OrgInnerTreeVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('at', Plug('OrgAInnerTreeVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].a_heading(skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('Ot', Plug('OrgOuterTreeVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(selection="outer", skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('OT', Plug('OrgAOuterTreeVisual', '<Esc>:<C-u>silent! py ORGMODE.plugins["Misc"].a_heading(selection="outer", skip_children=True)<CR>', mode=MODE_VISUAL)))

		self.keybindings.append(Keybinding('it', Plug('OrgInnerTreeOperator', ':<C-u>py ORGMODE.plugins["Misc"].i_heading(mode="operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('at', ':normal Vat<CR>', mode=MODE_OPERATOR))
		self.keybindings.append(Keybinding('Ot', Plug('OrgOuterTreeOperator', ':<C-u>silent! py ORGMODE.plugins["Misc"].i_heading(mode="operator", selection="outer", skip_children=True)<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('OT', ':normal VOT<CR>', mode=MODE_OPERATOR))
