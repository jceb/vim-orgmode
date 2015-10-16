# -*- coding: utf-8 -*-

import vim

from orgmode._vim import ORGMODE, apply_count
from orgmode.menu import Submenu
from orgmode.keybinding import Keybinding, Plug, MODE_VISUAL, MODE_OPERATOR


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
		if not heading or heading.start_vim != vim.current.window.cursor[0]:
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

	# @repeat
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

			line_start, col_start = [int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3]]
			line_end, col_end = [int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3]]

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
					vim.command(
						(u'normal! %dgg0%s%dgg$%s%s' %
							(start, visualmode, end, move_one_character_back, swap_cursor)).encode(u'utf-8'))
				else:
					vim.command(
						(u'normal! %dgg0%dl%s%dgg$%s%s' %
							(start, col_start - 1, visualmode, end, move_one_character_back, swap_cursor)).encode(u'utf-8'))
			else:
				vim.command(
					(u'normal! %dgg0%dl%s%dgg$%s%s' %
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

	# @repeat
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

			line_start, col_start = [int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3]]
			line_end, col_end = [int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3]]

			start = line_start
			end = line_end

			if heading.start_vim < line_start:
				start = heading.start_vim
			if heading.end_vim > line_end and not skip_children:
				end = heading.end_vim
			elif heading.end_of_last_child_vim > line_end and skip_children:
				end = heading.end_of_last_child_vim

			swap_cursor = u'o' if vim.current.window.cursor[0] == line_start else u''

			vim.command(
				(u'normal! %dgg%s%dgg$%s' %
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

# vim: set noexpandtab:
