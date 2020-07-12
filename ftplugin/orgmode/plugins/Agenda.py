# -*- coding: utf-8 -*-

from datetime import date
import os
import glob

import vim

from orgmode._vim import ORGMODE, get_bufnumber, get_bufname, echoe
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.menu import Submenu, ActionEntry, add_cmd_mapping_menu

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *
from orgmode.py3compat.py_py3_string import *

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
		cmds = [
			u'botright split org:%s' % bufname,
			u'setlocal buftype=nofile',
			u'setlocal modifiable',
			u'setlocal nonumber',
			# call opendoc() on enter the original todo item
			u'nnoremap <silent> <buffer> <CR> :exec "%s ORGMODE.plugins[u\'Agenda\'].opendoc()"<CR>' % VIM_PY_CALL,
			u'nnoremap <silent> <buffer> <TAB> :exec "%s ORGMODE.plugins[u\'Agenda\'].opendoc(switch=True)"<CR>' % VIM_PY_CALL,
			u'nnoremap <silent> <buffer> <S-CR> :exec "%s ORGMODE.plugins[u\'Agenda\'].opendoc(split=True)"<CR>' % VIM_PY_CALL,
			# statusline
			u'setlocal statusline=Org\\ %s' % bufname]
		if vim_commands:
			cmds.extend(vim_commands)
		for cmd in cmds:
			vim.command(u_encode(cmd))

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
			echoe(
				u"No org_agenda_files defined. Use :let "
				u"g:org_agenda_files=['~/org/index.org'] to add "
				u"files to the agenda view.")
			return
		return self._load_agendafiles(agenda_files)

	@classmethod
	def _load_agendafiles(self, agenda_files):
		# glob for files in agenda_files
		resolved_files = []
		for f in agenda_files:
			f = glob.glob(os.path.join(
				os.path.expanduser(os.path.dirname(f)),
				os.path.basename(f)))
			resolved_files.extend(f)

		agenda_files = [os.path.realpath(f) for f in resolved_files]

		# load the agenda files into buffers
		for agenda_file in agenda_files:
			vim.command(u_encode(u'badd %s' % agenda_file.replace(" ", "\\ ")))

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
			vim.command(u_encode(u'badd %s' % bufname))
			bufnr = get_bufnumber(bufname)
			tmp = cls.line2doc[row]
			cls.line2doc[bufnr] = tmp
			# delete old endry
			del cls.line2doc[row]

		if split:
			vim.command(u_encode(u"sbuffer %s" % bufnr))
		elif switch:
			vim.command(u_encode(u"wincmd w"))
			vim.command(u_encode(u"buffer %d" % bufnr))
		else:
			vim.command(u_encode(u"buffer %s" % bufnr))
		vim.command(u_encode(u"normal! %dgg <CR>" % (destrow + 1)))

	@classmethod
	def list_next_week(cls):
		agenda_documents = cls._get_agendadocuments()
		if not agenda_documents:
			return
		cls.list_next_week_for(agenda_documents)

	@classmethod
	def list_next_week_for_buffer(cls):
		agenda_documents = vim.current.buffer.name
		loaded_agendafiles = cls._load_agendafiles([agenda_documents])
		cls.list_next_week_for(loaded_agendafiles)


	@classmethod
	def list_next_week_for(cls, agenda_documents):
		raw_agenda = ORGMODE.agenda_manager.get_next_week_and_active_todo(
			agenda_documents)

		# if raw_agenda is empty, return directly
		if not raw_agenda:
			vim.command('echom "All caught-up. No agenda or active todo next week."')
			return

		# create buffer at bottom
		cmd = [u'setlocal filetype=orgagenda', ]
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

			bufname = os.path.basename(vim.buffers[h.document.bufnr].name)
			bufname = bufname[:-4] if bufname.endswith(u'.org') else bufname
			formatted = u"  %(bufname)s (%(bufnr)d)  %(todo)s  %(title)s" % {
				'bufname': bufname,
				'bufnr': h.document.bufnr,
				'todo': h.todo,
				'title': h.title
			}
			final_agenda.append(formatted)
			cls.line2doc[len(final_agenda)] = (get_bufname(h.document.bufnr), h.document.bufnr, h.start)

		# show agenda
		vim.current.buffer[:] = [u_encode(i) for i in final_agenda]
		vim.command(u_encode(u'setlocal nomodifiable  conceallevel=2 concealcursor=nc'))
		# try to jump to the position of today
		try:
			vim.command(u_encode(u'normal! %sgg<CR>' % today_row))
		except:
			pass

	@classmethod
	def list_all_todos(cls, current_buffer=False):
		u""" List all todos in one buffer.

		Args:
			current_buffer (bool):
				False: all agenda files
				True: current org_file
		"""
		if current_buffer:
			agenda_documents = vim.current.buffer.name
			loaded_agendafiles = cls._load_agendafiles([agenda_documents])
		else:
			loaded_agendafiles = cls._get_agendadocuments()
		if not loaded_agendafiles:
			return
		raw_agenda = ORGMODE.agenda_manager.get_todo(loaded_agendafiles)

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
		vim.current.buffer[:] = [u_encode(i) for i in final_agenda]
		vim.command(u_encode(u'setlocal nomodifiable  conceallevel=2 concealcursor=nc'))

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
		vim.current.buffer[:] = [u_encode(i) for i in final_agenda]
		vim.command(u_encode(u'setlocal nomodifiable conceallevel=2 concealcursor=nc'))

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		add_cmd_mapping_menu(
			self,
			name=u"OrgAgendaTodo",
			function=u'%s ORGMODE.plugins[u"Agenda"].list_all_todos()' % VIM_PY_CALL,
			key_mapping=u'<localleader>cat',
			menu_desrc=u'Agenda for all TODOs'
		)
		add_cmd_mapping_menu(
			self,
			name=u"OrgBufferAgendaTodo",
			function=u'%s ORGMODE.plugins[u"Agenda"].list_all_todos(current_buffer=True)' % VIM_PY_CALL,
			key_mapping=u'<localleader>caT',
			menu_desrc=u'Agenda for all TODOs based on current buffer'
		)
		add_cmd_mapping_menu(
			self,
			name=u"OrgAgendaWeek",
			function=u'%s ORGMODE.plugins[u"Agenda"].list_next_week()' % VIM_PY_CALL,
			key_mapping=u'<localleader>caa',
			menu_desrc=u'Agenda for the week'
		)
		add_cmd_mapping_menu(
			self,
			name=u"OrgBufferAgendaWeek",
			function=u'%s ORGMODE.plugins[u"Agenda"].list_next_week_for_buffer()' % VIM_PY_CALL,
			key_mapping=u'<localleader>caA',
			menu_desrc=u'Agenda for the week based on current buffer'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgAgendaTimeline',
			function=u'%s ORGMODE.plugins[u"Agenda"].list_timeline()' % VIM_PY_CALL,
			key_mapping=u'<localleader>caL',
			menu_desrc=u'Timeline for this buffer'
		)

# vim: set noexpandtab:
