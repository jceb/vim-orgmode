# -*- coding: utf-8 -*-
import re
from datetime import timedelta, date

import vim
from orgmode import ORGMODE, settings, echom
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry


class Date(object):
	"""
	Handles all date and timestamp related tasks.

	TODO: extend functionality (calendar, repetitions, ranges). See
	      http://orgmode.org/guide/Dates-and-Times.html#Dates-and-Times
	"""

	date_regex = r"\d\d\d\d-\d\d-\d\d"
	datetime_regex = r"[A-Z]\w\w \d\d\d\d-\d\d-\d\d \d\d:\d\d>"



	# set speeddating format that is compatible with orgmode
	try:
		if int(vim.eval('exists(":SpeedDatingFormat")')):
			vim.command(':1SpeedDatingFormat %Y-%m-%d %a')
			vim.command(':1SpeedDatingFormat %Y-%m-%d %a %H:%M')
		else:
			echom('Speeddating plugin not installed. Please install it.')
	except:
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
	def _modify_time(cls, startdate, modifier):
		if modifier is None:
			return startdate

		# check real date
		date_regex = r"(\d\d\d\d)-(\d\d)-(\d\d)"
		match = re. search(date_regex, modifier)
		if match:
			year, month, day =  match.groups()
			print match.groups()
			t = date(int(year), int(month), int(day))
			return t

		# check for days modifier
		match = re.search('\+(\d*)d', modifier)
		if match:
			days = int(match.groups()[0])
			return startdate + timedelta(days=days)

		# check for week modifier
		match = re.search('\+(\d+)w', modifier)
		if match:
			weeks = int(match.groups()[0])
			return startdate + timedelta(weeks=weeks)

		# check for week modifier
		match = re.search('\+(\d+)m', modifier)
		if match:
			months = int(match.groups()[0])
			return date(startdate.year, startdate.month + months, startdate.day)

		# check for year modifier
		match = re.search('\+(\d*)y', modifier)
		if match:
			years = int(match.groups()[0])
			return date(startdate.year + years, startdate.month, startdate.day)

		return startdate

	@classmethod
	def insert_timestamp(cls, active=True):
		"""
		Insert a timestamp (today) at the cursor position.

		TODO: show fancy calendar to pick the date from.
		"""
		today = date.today()
		msg = ''.join(['Insert Date: ', today.strftime('%Y-%m-%d %a'), ' | Change date'])
		change = Date.get_user_input(msg)
		echom(change)

		# check possible time modifications
		td = None
		if change.startswith('+'):
			try:
				if change.endswith('d'):
					td = timedelta(days=int(change[1:-1]))
				elif change.endswith('w'):
					td = timedelta(weeks=int(change[1:-1]))
			except:
				echom("Use integers to indicate the duration.")
				return

		# format
		if td:
			newdate = (today + td).strftime('%Y-%m-%d %a')
		else:
			newdate = today.strftime('%Y-%m-%d %a')
		timestamp = '<%s>' % newdate if active else '[%s]' % newdate

		Date.insert_at_cursor(timestamp)

	@staticmethod
	def insert_at_cursor(text):
		"""Insert text at the position of the cursor."""
		# TODO: Move to __init__
		col = vim.current.window.cursor[1]
		line = vim.current.line
		new_line = line[:col] + text + line[col:]
		vim.current.line = new_line

	@staticmethod
	def get_user_input(message):
		"""Print the message and take input from the user.
		Return the input from the user.

		TODO: move to __init__ or somewhere else where it makes more sense.
		"""
		vim.command('call inputsave()')
		vim.command("let user_input = input('" + message + ": ')")
		vim.command('call inputrestore()')
		return vim.eval('user_input')


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
