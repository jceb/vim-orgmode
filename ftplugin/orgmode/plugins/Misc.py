# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug
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

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding('^', Plug('OrgJumpToFirstCharacter', ':py ORGMODE.plugins["Misc"].jump_to_first_character()<CR>')))
		self.keybindings.append(Keybinding('I', Plug('OrgEditAtFirstCharacter', ':py ORGMODE.plugins["Misc"].edit_at_first_character()<CR>')))
