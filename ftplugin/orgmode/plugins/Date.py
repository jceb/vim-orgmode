# -*- coding: utf-8 -*-
import re
from datetime import timedelta, date, datetime
import calendar

import vim
from orgmode import ORGMODE, settings, echom, insert_at_cursor, get_user_input
from orgmode.keybinding import Keybinding, Plug
from orgmode.menu import Submenu, ActionEntry


class Date(object):
	u"""
	Handles all date and timestamp related tasks.

	TODO: extend functionality calendar view
	TODO: extend functionality repetitions
	TODO: extend functionality ranges.
	See http://orgmode.org/guide/Dates-and-Times.html#Dates-and-Times
	"""

	date_regex = r"\d\d\d\d-\d\d-\d\d"
	datetime_regex = r"[A-Z]\w\w \d\d\d\d-\d\d-\d\d \d\d:\d\d>"

	month_mapping = {u'jan': 1, u'feb': 2, u'mar': 3, u'apr': 4, u'may': 5,
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
			if int(vim.eval(u'exists(":SpeedDatingFormat")'.encode(u'utf-8'))):
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
			weekday_mapping = {u'mon': 0, u'tue': 1, u'wed': 2, u'thu': 3,
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
			return datetime(startdate.year, startdate.month, startdate.day,
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
		msg = u''.join([u'Inserting ',
				today.strftime(u'%Y-%m-%d %a'.encode(u'utf-8')),
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
	def show_calendar(cls):
		"""
		Show a calendar for the next three month at the bottom of the
		screen.
		"""
		# ensure we always start with a fresh buffer
		if bool(int(vim.eval(u'bufexists("org:calendar_view")'))):
			vim.command(u'au orgmode BufLeave <buffer> bwipeout org:calendar_view')

		# create a new calendar window
		# setup
		vim.command(u'setlocal noshowcmd')
		cmds = [u'botright 8split org:calendar_view',
				u'setlocal buftype=nofile',
				u'setlocal winfixheight',
				u'setlocal statusline=Calendar\\ no_functionality_yet',
				u'setlocal number',
				u'setlocal nonumber',
				u'setlocal nohlsearch',  # don't highlight search strings
				u'setlocal noinsertmode',  # don't make Insert mode the default
				u'setlocal noshowcmd',  # don't show command info on last line
				u'setlocal report=9999',  # don't show "X lines changed" reports
				u'setlocal sidescroll=0',  # don't sidescroll in jumps
				u'setlocal sidescrolloff=0',  # don't sidescroll automatically
				u'setlocal noequalalways',  # don't auto-balance window sizes
				u'setfiletype org_calendar',
				u'au orgmode BufLeave <buffer> bwipeout org:calendar_view',
				# mappings
				u'nnoremap <silent> <buffer> j w',  # jump to next day on j
				u'nnoremap <silent> <buffer> k b',  # jump to prev. day on k
				u'nnoremap <silent> <buffer> <Esc> :bwipeout org:calendar_view<CR>'
		]
		map(vim.command, cmds)

		# create the content of the calendar
		today = datetime.today()
		cal_str = Date._get_calendar_str(today.year, today.month)
		vim.current.buffer[:] = cal_str

		# set cursor to current day
		for row, row_data in enumerate(cal_str):
			# only look in the first month
			this_day = str(today.day)
			if this_day in row_data[:22]:
				col = row_data.index(this_day)
				break
		vim.current.window.cursor = (row + 1, col)

		# final setup
		cmds = [u'setlocal nomodifiable']
		map(vim.command, cmds)

	@classmethod
	def _get_calendar_str(cls, year, month):
		"""Generate a formated calendar string for the next three month."""

		# generate the first month str
		first = calendar.month(year, month, 2)

		# generate the second month str: inceremnt month (and year)
		month, year = (month + 1, year) if month < 12 else (1, year + 1)
		second = calendar.month(year, month, 2)

		# generate the third month str: incerment month (and year)
		month, year = (month + 1, year) if month < 12 else (1, year + 1)
		third = calendar.month(year, month, 2)

		# reformat them so that they are in one line
		result = []
		for m1, m2, m3 in zip(first.split('\n'), second.split('\n'),
				third.split('\n')):
			# append spaces if the line is too short
			m1 += (' ' * (25 - len(m1)))
			m2 += (' ' * (25 - len(m2)))
			result.append("".join([m1, m2, m3]))
		return result

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%ssa' % leader,
				Plug(u'OrgDateInsertTimestampActive',
				u':py ORGMODE.plugins[u"Date"].insert_timestamp()<CR>')))
		self.menu + ActionEntry(u'Timest&amp', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'%ssi' % leader,
				Plug(u'OrgDateInsertTimestampInactive',
					u':py ORGMODE.plugins[u"Date"].insert_timestamp(False)<CR>')))
		self.menu + ActionEntry(u'Timestamp (&inactive)', self.keybindings[-1])

		# TODO: rm this for release
		self.keybindings.append(Keybinding(u'%ssss' % leader,
				Plug(u'OrgShowCalendar',
				u':py ORGMODE.plugins[u"Date"].show_calendar()<CR>')))

		submenu = self.menu + Submenu(u'Change &Date')
		submenu + ActionEntry(u'Day &Earlier', u'<C-x>', u'<C-x>')
		submenu + ActionEntry(u'Day &Later', u'<C-a>', u'<C-a>')

# vim: set noexpandtab:
