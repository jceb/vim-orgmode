# -*- coding: utf-8 -*-
import re
from datetime import timedelta, date, datetime

import vim

from orgmode._vim import ORGMODE, echom, insert_at_cursor, get_user_input
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry, add_cmd_mapping_menu


class Date(object):
	u"""
	Handles all date and timestamp related tasks.

	TODO: extend functionality (calendar, repetitions, ranges). See
			http://orgmode.org/guide/Dates-and-Times.html#Dates-and-Times
	"""

	date_regex = r"\d\d\d\d-\d\d-\d\d"
	datetime_regex = r"[A-Z]\w\w \d\d\d\d-\d\d-\d\d \d\d:\d\d>"

	month_mapping = {
		u'jan': 1, u'feb': 2, u'mar': 3, u'apr': 4, u'may': 5,
		u'jun': 6, u'jul': 7, u'aug': 8, u'sep': 9, u'oct': 10, u'nov': 11,
		u'dec': 12}

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Dates and Scheduling')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

		# set speeddating format that is compatible with orgmode
		try:
			if int(vim.eval(u'exists(":SpeedDatingFormat")'.encode(u'utf-8'))) == 2:
				vim.command(u':1SpeedDatingFormat %Y-%m-%d %a'.encode(u'utf-8'))
				vim.command(u':1SpeedDatingFormat %Y-%m-%d %a %H:%M'.encode(u'utf-8'))
			else:
				echom(u'Speeddating plugin not installed. Please install it.')
		except:
			echom(u'Speeddating plugin not installed. Please install it.')

	@classmethod
	def _modify_time(cls, startdate, modifier):
		u"""Modify the given startdate according to modifier. Return the new
		date or datetime.

		See http://orgmode.org/manual/The-date_002ftime-prompt.html
		"""
		if modifier is None or modifier == '' or modifier == '.':
			return startdate

		# rm crap from modifier
		modifier = modifier.strip()

		# check real date
		date_regex = r"(\d\d\d\d)-(\d\d)-(\d\d)"
		match = re.search(date_regex, modifier)
		if match:
			year, month, day = match.groups()
			newdate = date(int(year), int(month), int(day))

		# check abbreviated date, seperated with '-'
		date_regex = u"(\d{1,2})-(\d+)-(\d+)"
		match = re.search(date_regex, modifier)
		if match:
			year, month, day = match.groups()
			newdate = date(2000 + int(year), int(month), int(day))

		# check abbreviated date, seperated with '/'
		# month/day
		date_regex = u"(\d{1,2})/(\d{1,2})"
		match = re.search(date_regex, modifier)
		if match:
			month, day = match.groups()
			newdate = date(startdate.year, int(month), int(day))
			# date should be always in the future
			if newdate < startdate:
				newdate = date(startdate.year + 1, int(month), int(day))

		# check full date, seperated with 'space'
		# month day year
		# 'sep 12 9' --> 2009 9 12
		date_regex = u"(\w\w\w) (\d{1,2}) (\d{1,2})"
		match = re.search(date_regex, modifier)
		if match:
			gr = match.groups()
			day = int(gr[1])
			month = int(cls.month_mapping[gr[0]])
			year = 2000 + int(gr[2])
			newdate = date(year, int(month), int(day))

		# check days as integers
		date_regex = u"^(\d{1,2})$"
		match = re.search(date_regex, modifier)
		if match:
			newday, = match.groups()
			newday = int(newday)
			if newday > startdate.day:
				newdate = date(startdate.year, startdate.month, newday)
			else:
				# TODO: DIRTY, fix this
				#       this does NOT cover all edge cases
				newdate = startdate + timedelta(days=28)
				newdate = date(newdate.year, newdate.month, newday)

		# check for full days: Mon, Tue, Wed, Thu, Fri, Sat, Sun
		modifier_lc = modifier.lower()
		match = re.search(u'mon|tue|wed|thu|fri|sat|sun', modifier_lc)
		if match:
			weekday_mapping = {
				u'mon': 0, u'tue': 1, u'wed': 2, u'thu': 3,
				u'fri': 4, u'sat': 5, u'sun': 6}
			diff = (weekday_mapping[modifier_lc] - startdate.weekday()) % 7
			# use next weeks weekday if current weekday is the same as modifier
			if diff == 0:
				diff = 7
			newdate = startdate + timedelta(days=diff)

		# check for days modifier with appended d
		match = re.search(u'\+(\d*)d', modifier)
		if match:
			days = int(match.groups()[0])
			newdate = startdate + timedelta(days=days)

		# check for days modifier without appended d
		match = re.search(u'\+(\d*) |\+(\d*)$', modifier)
		if match:
			try:
				days = int(match.groups()[0])
			except:
				days = int(match.groups()[1])
			newdate = startdate + timedelta(days=days)

		# check for week modifier
		match = re.search(u'\+(\d+)w', modifier)
		if match:
			weeks = int(match.groups()[0])
			newdate = startdate + timedelta(weeks=weeks)

		# check for week modifier
		match = re.search(u'\+(\d+)m', modifier)
		if match:
			months = int(match.groups()[0])
			newdate = date(startdate.year, startdate.month + months, startdate.day)

		# check for year modifier
		match = re.search(u'\+(\d*)y', modifier)
		if match:
			years = int(match.groups()[0])
			newdate = date(startdate.year + years, startdate.month, startdate.day)

		# check for month day
		match = re.search(
			u'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) (\d{1,2})',
			modifier.lower())
		if match:
			month = cls.month_mapping[match.groups()[0]]
			day = int(match.groups()[1])
			newdate = date(startdate.year, int(month), int(day))
			# date should be always in the future
			if newdate < startdate:
				newdate = date(startdate.year + 1, int(month), int(day))

		# check abbreviated date, seperated with '/'
		# month/day/year
		date_regex = u"(\d{1,2})/(\d+)/(\d+)"
		match = re.search(date_regex, modifier)
		if match:
			month, day, year = match.groups()
			newdate = date(2000 + int(year), int(month), int(day))

		# check for month day year
		# sep 12 2011
		match = re.search(
			u'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec) (\d{1,2}) (\d{1,4})',
			modifier.lower())
		if match:
			month = int(cls.month_mapping[match.groups()[0]])
			day = int(match.groups()[1])
			if len(match.groups()[2]) < 4:
				year = 2000 + int(match.groups()[2])
			else:
				year = int(match.groups()[2])
			newdate = date(year, month, day)

		# check for time: HH:MM
		# '12:45' --> datetime(2006, 06, 13, 12, 45))
		match = re.search(u'(\d{1,2}):(\d\d)$', modifier)
		if match:
			try:
				startdate = newdate
			except:
				pass
			return datetime(
				startdate.year, startdate.month, startdate.day,
				int(match.groups()[0]), int(match.groups()[1]))

		try:
			return newdate
		except:
			return startdate

	@classmethod
	def insert_timestamp(cls, active=True):
		u"""
		Insert a timestamp at the cursor position.

		TODO: show fancy calendar to pick the date from.
		TODO: add all modifier of orgmode.
		"""
		today = date.today()
		msg = u''.join([
			u'Inserting ',
			unicode(today.strftime(u'%Y-%m-%d %a'), u'utf-8'),
			u' | Modify date'])
		modifier = get_user_input(msg)

		# abort if the user canceled the input promt
		if modifier is None:
			return

		newdate = cls._modify_time(today, modifier)

		# format
		if isinstance(newdate, datetime):
			newdate = newdate.strftime(
				u'%Y-%m-%d %a %H:%M'.encode(u'utf-8')).decode(u'utf-8')
		else:
			newdate = newdate.strftime(
				u'%Y-%m-%d %a'.encode(u'utf-8')).decode(u'utf-8')
		timestamp = u'<%s>' % newdate if active else u'[%s]' % newdate

		insert_at_cursor(timestamp)

	@classmethod
	def insert_timestamp_with_calendar(cls, active=True):
		u"""
		Insert a timestamp at the cursor position.
		Show fancy calendar to pick the date from.

		TODO: add all modifier of orgmode.
		"""
		if int(vim.eval(u'exists(":CalendarH")'.encode(u'utf-8'))) != 2:
			vim.command("echo 'Please install plugin Calendar to enable this function'")
			return
		vim.command("CalendarH")
		# backup calendar_action
		calendar_action = vim.eval("g:calendar_action")
		vim.command("let g:org_calendar_action_backup = '" + calendar_action + "'")
		vim.command("let g:calendar_action = 'CalendarAction'")

		timestamp_template = u'<%s>' if active else u'[%s]'
		# timestamp template
		vim.command("let g:org_timestamp_template = '" + timestamp_template + "'")

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		add_cmd_mapping_menu(
			self,
			name=u'OrgDateInsertTimestampActiveCmdLine',
			key_mapping=u'<localleader>sa',
			function=u':py ORGMODE.plugins[u"Date"].insert_timestamp()',
			menu_desrc=u'Timest&amp'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgDateInsertTimestampInactiveCmdLine',
			key_mapping='<localleader>si',
			function=u':py ORGMODE.plugins[u"Date"].insert_timestamp(False)',
			menu_desrc=u'Timestamp (&inactive)'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgDateInsertTimestampActiveWithCalendar',
			key_mapping=u'<localleader>pa',
			function=u':py ORGMODE.plugins[u"Date"].insert_timestamp_with_calendar()',
			menu_desrc=u'Timestamp with Calendar'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgDateInsertTimestampInactiveWithCalendar',
			key_mapping=u'<localleader>pi',
			function=u':py ORGMODE.plugins[u"Date"].insert_timestamp_with_calendar(False)',
			menu_desrc=u'Timestamp with Calendar(inactive)'
		)

		submenu = self.menu + Submenu(u'Change &Date')
		submenu + ActionEntry(u'Day &Earlier', u'<C-x>', u'<C-x>')
		submenu + ActionEntry(u'Day &Later', u'<C-a>', u'<C-a>')

# vim: set noexpandtab:
