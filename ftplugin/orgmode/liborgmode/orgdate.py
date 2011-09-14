# -*- coding: utf-8 -*-
u"""
	OrgDate
	~~~~~~~~~~~~~~~~~~

	This module contains all date/time/timerange representations that exist in
	orgmode.

	There exist three different kinds:

	* OrgDate: is similar to a date object in python and it looks like
	  '2011-09-07 Wed'.

	* OrgDateTime: is similar to a datetime object in python and looks like
	  '2011-09-07 Wed 10:30'

	* OrgTimeRange: indicates a range of time. It has a start and and end date:
	  * <2011-09-07 Wed>--<2011-09-08 Fri>
	  * <2011-09-07 Wed 10:00-13:00>

	All OrgTime oblects can be active or inactive.
"""

import datetime
import re

# <2011-09-12 Mon>
_DATE_REGEX = re.compile(r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>")
# [2011-09-12 Mon]
_DATE_PASSIVE_REGEX = re.compile(r"\[(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w\]")

# <2011-09-12 Mon 10:20>
_DATETIME_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d{1,2}):(\d\d)>")
# [2011-09-12 Mon 10:20]
_DATETIME_PASSIVE_REGEX = re.compile(
		r"\[(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d{1,2}):(\d\d)\]")

# <2011-09-12 Mon>--<2011-09-13 Tue>
_DATERANGE_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>--<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w>")
# <2011-09-12 Mon 10:00>--<2011-09-12 Mon 11:00>
_DATETIMERANGE_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)>--<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)>")
# <2011-09-12 Mon 10:00--12:00>
_DATETIMERANGE_SAME_DAY_REGEX = re.compile(
		r"<(\d\d\d\d)-(\d\d)-(\d\d) [A-Z]\w\w (\d\d):(\d\d)-(\d\d):(\d\d)>")


def get_orgdate(data):
	u"""
	Parse the given data (can be a string or list). Return an OrgDate if data
	contains a string representation of an OrgDate; otherwise return None.

	data can be a string or a list containing strings.
	"""
	if isinstance(data, list):
		return _findfirst(_text2orgdate, data)
	else:
		return _text2orgdate(data)
	# if no dates found
	return None


def _findfirst(f, seq):
	u"""
	Return first item in sequence seq where f(item) == True.

	TODO: this is a general help function and it should be moved somewhere
	else; preferably into the standard lib :)
	"""
	for found in (f(item) for item in seq if f(item)):
		return found


def _text2orgdate(string):
	u"""
	Transform the given string into an OrgDate.
	Return an OrgDate if data contains a string representation of an OrgDate;
	otherwise return None.
	"""
	# handle active datetime with same day
	result = _DATETIMERANGE_SAME_DAY_REGEX.search(string)
	if result:
		try:
			(syear, smonth, sday, shour, smin, ehour, emin) = \
					[int(m) for m in result.groups()]
			start = datetime.datetime(syear, smonth, sday, shour, smin)
			end = datetime.datetime(syear, smonth, sday, ehour, emin)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATETIMERANGE_REGEX.search(string)
	if result:
		try:
			(syear, smonth, sday, shour, smin,
					eyear, emonth, eday, ehour, emin) = [int(m) for m in result.groups()]
			start = datetime.datetime(syear, smonth, sday, shour, smin)
			end = datetime.datetime(eyear, emonth, eday, ehour, emin)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATERANGE_REGEX.search(string)
	if result:
		try:
			syear, smonth, sday, eyear, emonth, ehour = [int(m) for m in result.groups()]
			start = datetime.date(syear, smonth, sday)
			end = datetime.date(eyear, emonth, ehour)
			return OrgTimeRange(True, start, end)
		except Exception:
			return None

	# handle active datetime
	result = _DATETIME_REGEX.search(string)
	if result:
		try:
			year, month, day, hour, minutes = [int(m) for m in result.groups()]
			return OrgDateTime(True, year, month, day, hour, minutes)
		except Exception:
			return None

	# handle passive datetime
	result = _DATETIME_PASSIVE_REGEX.search(string)
	if result:
		try:
			year, month, day, hour, minutes = [int(m) for m in result.groups()]
			return OrgDateTime(False, year, month, day, hour, minutes)
		except Exception:
			return None

	# handle passive dates
	result = _DATE_PASSIVE_REGEX.search(string)
	if result:
		try:
			year, month, day = [int(m) for m in result.groups()]
			return OrgDate(False, year, month, day)
		except Exception:
			return None

	# handle active dates
	result = _DATE_REGEX.search(string)
	if result:
		try:
			year, month, day = [int(m) for m in result.groups()]
			return OrgDate(True, year, month, day)
		except Exception:
			return None


class OrgDate(datetime.date):
	u"""
	OrgDate represents a normal date like '2011-08-29 Mon'.

	OrgDates can be active or inactive.

	NOTE: date is immutable. Thats why there needs to be __new__().
	See: http://docs.python.org/reference/datamodel.html#object.__new__
	"""
	def __init__(self, active, year, month, day):
		self.active = active
		pass

	def __new__(cls, active, year, month, day):
		return datetime.date.__new__(cls, year, month, day)

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		if self.active:
			return self.strftime(u'<%Y-%m-%d %a>')
		else:
			return self.strftime(u'[%Y-%m-%d %a]')

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')


class OrgDateTime(datetime.datetime):
	u"""
	OrgDateTime represents a normal date like '2011-08-29 Mon'.

	OrgDateTime can be active or inactive.

	NOTE: date is immutable. Thats why there needs to be __new__().
	See: http://docs.python.org/reference/datamodel.html#object.__new__
	"""

	def __init__(self, active, year, month, day, hour, mins):
		self.active = active

	def __new__(cls, active, year, month, day, hour, minute):
		return datetime.datetime.__new__(cls, year, month, day, hour, minute)

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		if self.active:
			return self.strftime(u'<%Y-%m-%d %a %H:%M>')
		else:
			return self.strftime(u'[%Y-%m-%d %a %H:%M]')

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')


class OrgTimeRange(object):
	u"""
	OrgTimeRange objects have a start and an end. Start and ent can be date
	or datetime. Start and end have to be the same type.

	OrgTimeRange objects look like this:
	* <2011-09-07 Wed>--<2011-09-08 Fri>
	* <2011-09-07 Wed 20:00>--<2011-09-08 Fri 10:00>
	* <2011-09-07 Wed 10:00-13:00>
	"""

	def __init__(self, active, start, end):
		u"""
		stat and end must be datetime.date or datetime.datetime (both of the
		same type).
		"""
		super(OrgTimeRange, self).__init__()
		self.start = start
		self.end = end
		self.active = active

	def __unicode__(self):
		u"""
		Return a string representation.
		"""
		# active
		if self.active:
			# datetime
			if isinstance(self.start, datetime.datetime):
				# if start and end are on same the day
				if self.start.year == self.end.year and\
						self.start.month == self.end.month and\
						self.start.day == self.end.day:
					return u"<%s-%s>" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%H:%M'))
				else:
					return u"<%s>--<%s>" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%Y-%m-%d %a %H:%M'))
			# date
			if isinstance(self.start, datetime.date):
				return u"<%s>--<%s>" % (self.start.strftime(u'%Y-%m-%d %a'),
						self.end.strftime(u'%Y-%m-%d %a'))
		# inactive
		else:
			if isinstance(self.start, datetime.datetime):
				# if start and end are on same the day
				if self.start.year == self.end.year and\
						self.start.month == self.end.month and\
						self.start.day == self.end.day:
					return u"[%s-%s]" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%H:%M'))
				else:
					return u"[%s]--[%s]" % (
							self.start.strftime(u'%Y-%m-%d %a %H:%M'),
							self.end.strftime(u'%Y-%m-%d %a %H:%M'))
			if isinstance(self.start, datetime.date):
				return u"[%s]--[%s]" % (self.start.strftime(u'%Y-%m-%d %a'),
						self.end.strftime(u'%Y-%m-%d %a'))

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

# vim: set noexpandtab:
