# -*- coding: utf-8 -*-

from datetime import date
import os

from orgmode import ORGMODE, settings
from orgmode import get_bufnumber
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
				u'nnoremap <silent> <buffer> <CR> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc()"<CR>'.encode(u'utf-8'),
				u'nnoremap <silent> <buffer> <TAB> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc(switch=True)"<CR>'.encode(u'utf-8'),
				u'nnoremap <silent> <buffer> <S-CR> :exec "py ORGMODE.plugins[u\'Agenda\'].opendoc(split=True)"<CR>'.encode(u'utf-8'),
				# statusline
				u'setlocal statusline=Org\\ %s' % bufname
				]
		if vim_commands:
			cmds.extend(vim_commands)
		for cmd in cmds:
			vim.command(cmd)

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
			echoe("No org_agenda_files defined. Use \
:let g:org_agenda_files=['~/org/index.org'] to add \
files to the agenda view.")
			return
		agenda_files = [os.path.expanduser(f) for f in agenda_files]
		for agenda_file in agenda_files:
			vim.command('badd %s' % agenda_file)

		# determine the buffer nr of the agenda files
		agenda_numbers = [get_bufnumber(fn) for fn in agenda_files]

		# collect all documents of the agenda files and create the agenda
		return [ORGMODE.get_document(i) for i in agenda_numbers]

	@classmethod
	def opendoc(cls, split=False, switch=False):
		"""
		If you are in the agenda view jump to the document the item in the
		current line belongs to. cls.line2doc is used for that.

		:split: if True, open the document in a new split window.
		:switch: if True, switch to another window and open the the document
			there.
		"""
		row, _ = vim.current.window.cursor
		try:
			bufnr, destrow = cls.line2doc[row]
		except:
			return

		if split:
			vim.command("sbuffer %s" % bufnr)
		elif switch:
			vim.command('wincmd w')
			vim.command("buffer %s" % bufnr)
		else:
			vim.command("buffer %s" % bufnr)
		vim.command("normal! %sgg <CR>" % str(destrow + 1))

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
		cls._switch_to('AGENDA', cmd)

		# line2doc is a dic with the mapping:
		#     line in agenda buffer --> source document
		# It's easy to jump to the right document this way
		cls.line2doc = {}
		# format text for agenda
		last_date = raw_agenda[0].active_date
		final_agenda = ['Week Agenda:', str(last_date)]
		for i, h in enumerate(raw_agenda):
			# insert date information for every new date
			if str(h.active_date)[1:11] != str(last_date)[1:11]:
				today = date.today()
				# insert additional "TODAY" string
				if h.active_date.year == today.year and \
						h.active_date.month == today.month and \
						h.active_date.day == today.day:
					section = str(h.active_date) + " TODAY"
					today_row = len(final_agenda) + 1
				else:
					section = str(h.active_date)
				final_agenda.append(section)

				# update last_date
				last_date = h.active_date

			bufname = os.path.basename(vim.buffers[h.document.bufnr-1].name)
			bufname = bufname[:-4] if bufname.endswith('.org') else bufname
			formated = "  {bufname} ({bufnr})  {todo}  {title}".format(
					bufname=bufname,
					bufnr=str(h.document.bufnr),
					todo=str(h.todo),
					title=str(h.title)
			)
			final_agenda.append(formated)
			cls.line2doc[len(final_agenda)] = (h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = final_agenda
		vim.command(u'setlocal nomodifiable')
		# try to jump to the positon of today
		try:
			vim.command('normal %sgg<CR>' % today_row)
		except:
			pass

	@classmethod
	def list_all_todos(cls):
		"""
		List all todos in all agenda files in one buffer.
		"""
		agenda_documents = cls._get_agendadocuments()
		if not agenda_documents:
			return
		raw_agenda = ORGMODE.agenda_manager.get_todo(agenda_documents)

		cls.line2doc = {}
		# create buffer at bottom
		cmd = [u'setlocal filetype=orgagenda']
		cls._switch_to('AGENDA', cmd)

		# format text of agenda
		final_agenda = []
		for i, h in enumerate(raw_agenda):
			tmp = "%s %s" % (str(h.todo).encode(u'utf-8'),
					str(h.title).encode(u'utf-8'))
			final_agenda.append(tmp)
			cls.line2doc[len(final_agenda)] = (h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = final_agenda
		vim.command(u'setlocal nomodifiable')

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
		cls._switch_to('AGENDA', cmd)

		cls.line2doc = {}
		# format text of agenda
		final_agenda = []
		for i, h in enumerate(raw_agenda):
			tmp = "%s %s" % (str(h.todo).encode(u'utf-8'),
					str(h.title).encode(u'utf-8'))
			final_agenda.append(tmp)
			cls.line2doc[len(final_agenda)] = (h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = final_agenda
		vim.command(u'setlocal nomodifiable conceallevel=2 concealcursor=nc')

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

		self.keybindings.append(Keybinding(u'%scaL' % leader,
				Plug(u'OrgAgendaTimeline',
				u':py ORGMODE.plugins[u"Agenda"].list_timeline()<CR>')))
		self.menu + ActionEntry(u'Timeline for this buffer',
				self.keybindings[-1])

# vim: set noexpandtab:
