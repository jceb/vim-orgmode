# -*- coding: utf-8 -*-
import re

import vim
from orgmode import ORGMODE, settings, echom, insert_at_cursor, get_user_input
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry


class Agenda(object):
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
	def test(cls):
		pass

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%sca' % leader,
				Plug(u'OrgAgendaTest',
				u':py ORGMODE.plugins[u"Agenda"].test()<CR>')))
		self.menu + ActionEntry(u'Test', self.keybindings[-1])

# vim: set noexpandtab:
