# -*- coding: utf-8 -*-

import vim

from datetime import *

from orgmode._vim import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry, add_cmd_mapping_menu
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.liborgmode.headings import ClockLine
from orgmode.liborgmode.orgdate import OrgDateTime, OrgTimeRange

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.py_py3_string import *
from orgmode.py3compat.unicode_compatibility import *


def get_total_time(heading):
	total = None
	for clockline in heading.logbook:
		if not clockline.finished:
			continue

		if total is None:
			total = clockline.date.duration()
		else:
			total += clockline.date.duration()

	for child in heading.children:
		if total is None:
			total = get_total_time(child)
		else:
			total += get_total_time(child)

	return total


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
	def clock_in(cls):
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		current_heading.init_logbook()

		now = datetime.now()
		new_clock_line = ClockLine(
			date=OrgDateTime(False, now.year, now.month, now.day, now.hour, now.minute),
			level=current_heading.level + 1
		)
		current_heading.logbook.append(new_clock_line)

		# + 1 line to skip the heading itself
		start = current_heading.start + 1
		if len(current_heading.logbook) == 1:
			vim.current.buffer[start:start] = [u' ' * current_heading.level + u':LOGBOOK:']

		# For ':LOGBOOK:' line
		start += 1
		vim.current.buffer[start:start] = [unicode(new_clock_line)]

		if len(current_heading.logbook) == 1:
			start += 1
			vim.current.buffer[start:start] = [u' ' * current_heading.level + u':END:']

	@classmethod
	def clock_out(cls):
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		current_heading.init_logbook()

		if not current_heading.logbook:
			return

		for last_entry in current_heading.logbook:
			if not last_entry.finished:
				break
		else:
			return

		end_date = datetime.now()
		duration = OrgTimeRange(False, last_entry.date, end_date)
		last_entry.date = duration

		d.write_clockline(last_entry)

	@classmethod
	def clock_update(cls):
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		current_heading.init_logbook()

		if not current_heading.logbook:
			return

		position = vim.current.window.cursor[0] - 1
		# -2 to skip heading itself and :LOGBOOK:
		clockline_index = position - current_heading.start - 2

		if clockline_index < 0 or clockline_index >= len(current_heading.logbook):
			return

		current_heading.logbook[clockline_index].set_dirty()

		d.write_clockline(current_heading.logbook[clockline_index])

	@classmethod
	def clock_total(cls):
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		current_heading.init_logbook()

		total = get_total_time(current_heading)

		if total is not None:
			hours, minutes = divmod(total.total_seconds(), 3600)
			echo(u'Total time spent in this heading: %d:%d' % (hours, minutes // 60))

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		add_cmd_mapping_menu(
			self,
			name=u'OrgLoggingClockIn',
			function=u'%s ORGMODE.plugins[u"LoggingWork"].clock_in()<CR>' % VIM_PY_CALL,
			key_mapping=u'<localleader>ci',
			menu_desrc=u'Clock in'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgLoggingClockOut',
			function=u'%s ORGMODE.plugins[u"LoggingWork"].clock_out()<CR>' % VIM_PY_CALL,
			key_mapping=u'<localleader>co',
			menu_desrc=u'Clock out'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgLoggingClockUpdate',
			function=u'%s ORGMODE.plugins[u"LoggingWork"].clock_update()<CR>' % VIM_PY_CALL,
			key_mapping=u'<localleader>cu',
			menu_desrc=u'Clock update'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgLoggingClockTotal',
			function=u'%s ORGMODE.plugins[u"LoggingWork"].clock_total()<CR>' % VIM_PY_CALL,
			key_mapping=u'<localleader>ct',
			menu_desrc=u'Show total clocked time for the current heading'
		)
