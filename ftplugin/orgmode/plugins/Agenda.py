# -*- coding: utf-8 -*-

from datetime import date

from orgmode import ORGMODE, settings
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry
import vim

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
	def _switch_to(cls, bufname, vim_commands=None):
		"""
		Swicht to the buffer with bufname.

		A list of vim.commands (if given) gets executed as well.

		TODO: this should be extracted and imporved to create an easy to use
		way to create buffers/jump to buffers. Otherwise there are going to be
		quite a few ways to open buffers in vimorgmode.
		"""
		cmds = [u'botright split org:%s' % bufname,
				u'setlocal buftype=nofile',
				u'setlocal modifiable',
				u'setlocal statusline=Org\\ %s' % bufname
				]
		if vim_commands:
			cmds.extend(vim_commands)
		for cmd in cmds:
			vim.command(cmd)

	@classmethod
	def list_next_week(cls):
		agenda_files = settings.get(u'org_agenda_files', u',')
		for agenda_file in agenda_files:
			vim.command('badd %s' % agenda_file)
		# TODO: this only works when orgmode is started with one orgfile
		# how can I get the number of a buffer with a given name
		agenda_documents = [ORGMODE.get_document(i+1) for i in range(len(agenda_files))]

		# get agenda
		raw_agenda = ORGMODE.agenda_manager.get_next_week_and_active_todo(agenda_documents)

		# create buffer at bottom
		cmd = [u'setlocal filetype=orgtodo']
		cls._switch_to('AGENDA', cmd)

		# format text for agenda
		last_date = raw_agenda[0].active_date
		final_agenda = [str(last_date)]
		for i, h in enumerate(raw_agenda):
			# insert date information for every new date
			if h.active_date != last_date:
				today = date.today()
				# insert additional "TODAY" string
				if h.active_date.year == today.year and \
						h.active_date.month == today.month and \
						h.active_date.day == today.day:
					section = str(h.active_date) + " TODAY"
				else:
					section = str(h.active_date)
				final_agenda.append(section)

				# update last_date
				last_date = h.active_date

			tmp = "  %s %s" % (str(h.todo), str(h.title))
			final_agenda.append(tmp)

		# show agenda
		print final_agenda
		vim.current.buffer[:] = final_agenda
		vim.command(u'setlocal nomodifiable')

	@classmethod
	def list_all_todos(cls):
		# make sure the agenda file is loaded
		agenda_files = settings.get(u'org_agenda_files', u',')
		for agenda_file in agenda_files:
			vim.command('badd %s' % agenda_file)
		# TODO: this only works when orgmode is started with one orgfile
		# how can I get the number of a buffer with a given name
		agenda_documents = [ORGMODE.get_document(i+1) for i in range(len(agenda_files))]

		# get agenda
		raw_agenda = ORGMODE.agenda_manager.get_todo(agenda_documents)

		# create buffer at bottom
		cmd = [u'setlocal filetype=orgtodo']
		cls._switch_to('AGENDA', cmd)

		# format text of agenda
		final_agenda = []
		for i, h in enumerate(raw_agenda):
			tmp = "%s %s" % (str(h.todo).encode(u'utf-8'), str(h.title).encode(u'utf-8'))
			final_agenda.append(tmp)

		# show agenda
		vim.current.buffer[:] = final_agenda
		vim.command(u'setlocal nomodifiable')

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%scat' % leader,
				Plug(u'OrgAgendaTodo',
				u':py ORGMODE.plugins[u"Agenda"].list_all_todos()<CR>')))
		self.menu + ActionEntry(u'Agenda for all TODOs', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'%scaa' % leader,
				Plug(u'OrgAgendaWeek',
				u':py ORGMODE.plugins[u"Agenda"].list_next_week()<CR>')))
		self.menu + ActionEntry(u'Agenda for the week', self.keybindings[-1])

		# set agend files
		settings.set(u'org_agenda_files', [u'~/org/index.org'.encode(u'utf-8'), '~/org/TodaY.org'.encode(u'utf-8')])
# vim: set noexpandtab:
