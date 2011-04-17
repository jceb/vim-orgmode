# -*- coding: utf-8 -*-

from orgmode import ORGMODE
from orgmode import settings
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug

import vim

from orgmode import echom
from datetime import date
#import re


class Date(object):
	"""
	Handles all date and timestamp related tasks.

	TODO: extend functionality (calendar, repetitions, ranges). See
	      http://orgmode.org/guide/Dates-and-Times.html#Dates-and-Times
	"""

	date_regex = r"<[A-z]\w\w \d\d\d\d-\d\d-\d\d>"
	datetime_regex = r"<[A-z]\w\w \d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d>"

	# set speeddating format that is compatible with orgmode
	if int(vim.eval('exists(":SpeedDatingFormat")')):
		vim.command(':1SpeedDatingFormat %Y-%m-%d %a')
	else:
		echom('Speeddating plugin not installed. Please install it.')

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('Dates and Scheduling')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def insert_timestamp(cls, active=True):
		"""
		Insert a timestamp (today) at the cursor position.

		TODO: show fancy calendar to pick the date from.
		"""
		if active:
			timestamp = '<%s>' % date.today().strftime('%Y-%m-%d %a')
		else:
			timestamp = '[%s]' % date.today().strftime('%Y-%m-%d %a')
		row, col = vim.current.window.cursor
		line = vim.current.line
		new_line = line[:col] + timestamp + line[col:]
		vim.current.line = new_line

	def register(self):
		"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		settings.set('org_leader', ',')
		leader = settings.get('org_leader', ',')

		self.keybindings.append(Keybinding('%stn' % leader,
				Plug('OrgDateInsertTimestampActive',
				':py ORGMODE.plugins["Date"].insert_timestamp()<CR>')))
		self.menu + ActionEntry('Timestamp', self.keybindings[-1])

		self.keybindings.append(Keybinding('%sti' % leader,
				Plug('OrgDateInsertTimestampInactive', ':py ORGMODE.plugins["Date"].insert_timestamp(False)<CR>')))
		self.menu + ActionEntry('Timestamp (inactive)', self.keybindings[-1])

# vim: set noexpandtab:
