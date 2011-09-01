# -*- coding: utf-8 -*-
from orgmode import ORGMODE, settings, echom
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
		agenda = ORGMODE.get_agenda()
		print "test agenda"
		print "=" * 30
		print
		print len(agenda)
		for i, item in enumerate(agenda):
			echom(item.title)


	@classmethod
	def list_all_todos(cls):
		agenda = ORGMODE.get_agenda_TODO()
		print "TODO agenda"
		print "=" * 30
		print
		# create buffer at bottom
		# ORG_AGENDA

		# format text for agenda
		print len(agenda)
		for i, item in enumerate(agenda):
			echom(item.title)

		# show agenda


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

		self.keybindings.append(Keybinding(u'%scat' % leader,
				Plug(u'OrgAgendaTodo',
				u':py ORGMODE.plugins[u"Agenda"].list_all_todos()<CR>')))
		self.menu + ActionEntry(u'Test', self.keybindings[-1])

# vim: set noexpandtab:
