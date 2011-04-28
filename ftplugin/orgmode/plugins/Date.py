# -*- coding: utf-8 -*-
import re
from datetime import timedelta, date

import vim
from orgmode import ORGMODE, settings, echom, insert_at_cursor, get_user_input
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
		"""Modify the given startdate according to modifier. Return the new time.

		See http://orgmode.org/manual/The-date_002ftime-prompt.html#The-date_002ftime-prompt
		"""
		if modifier is None:
			return startdate

		# check real date
		date_regex = r"(\d\d\d\d)-(\d\d)-(\d\d)"
		match = re. search(date_regex, modifier)
		if match:
			year, month, day =  match.groups()
			t = date(int(year), int(month), int(day))
			return t

		# check abbreviated date, seperated with '-'
		date_regex = "(\d{1,2})-(\d+)-(\d+)"
		match = re. search(date_regex, modifier)
		if match:
			year, month, day =  match.groups()
			t = date(2000+int(year), int(month), int(day))
			return t

		# check abbreviated date, seperated with '/'
		# month/day/year
		date_regex = "(\d{1,2})/(\d+)/(\d+)"
		match = re. search(date_regex, modifier)
		if match:
			month, day, year =  match.groups()
			t = date(2000+int(year), int(month), int(day))
			return t

		# check day
		date_regex = "^(\d{1,2})$"
		match = re. search(date_regex, modifier)
		if match:
			newday, =  match.groups()
			newday =  int(newday)
			if newday > startdate.day:
				newdate = date(startdate.year, startdate.month, newday)
			else:
				# TODO: DIRTY, fix this
				#       this does NOT cover all edge cases
				newdate = startdate + timedelta(days=28)
				newdate = date(newdate.year, newdate.month, newday)
			return newdate

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
		modifier = get_user_input(msg)
		echom(modifier)

		newdate = cls._modify_time(today, modifier)

		# format
		newdate = newdate.strftime('%Y-%m-%d %a')
		timestamp = '<%s>' % newdate if active else '[%s]' % newdate

		insert_at_cursor(timestamp)

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
