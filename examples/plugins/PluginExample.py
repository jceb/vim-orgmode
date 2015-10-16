# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command

import vim


class Example(object):
	u"""
	Example plugin.

	TODO: Extend this doc!
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Example')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def action(cls):
		u"""
		Some kind of action.

		:returns: TODO
		"""
		pass

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		self.commands.append(Command(u'OrgActionCommand',
				u':py ORGMODE.plugins["Example"].action()'))
		self.keybindings.append(Keybinding(u'keybinding',
				Plug(u'OrgAction', self.commands[-1])))
		self.menu + ActionEntry(u'&Action', self.keybindings[-1])

# vim: set noexpandtab:
