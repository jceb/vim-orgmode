# -*- coding: utf-8 -*-

u"""
	agendafilter
	~~~~~~~~~~~~~~~~

	AgendaFilter contains all the filters that can be applied to create the
	agenda.


	All functions except filter_items() in the module are filters. Given a
	heading they return if the heading meets the critera of the filter.

	The function filter_items() can combine different filters and only returns
	the filtered headings.
"""

from datetime import date
from datetime import datetime
from datetime import timedelta


def filter_items(headings, filters):
	u"""
	Filter the given headings. Return the list of headings which were not
	filtered.

	:headings: is an list of headings
	:filters: is the list of filters that are to be applied. all function in
			this module (except this function) are filters.

	You can use it like this:

	>>> filtered = filter_items(headings, [contains_active_date,
				contains_active_todo])

	"""
	filtered = headings
	for f in filters:
		filtered = filter(f, filtered)
	return filtered


def is_within_week(heading):
	u"""
	Return True if the date in the deading is within a week in the future (or
	older.
	"""
	if contains_active_date(heading):
		next_week = datetime.today() + timedelta(days=7)
		if heading.active_date < next_week:
			return True


def is_within_week_and_active_todo(heading):
	u"""
	Return True if heading contains an active TODO and the date is within a
	week.
	"""
	return is_within_week(heading) and contains_active_todo(heading)


def contains_active_todo(heading):
	u"""
	Return True if heading contains an active TODO.

	FIXME: the todo checking should consider a number of different active todo
	states
	"""
	return heading.todo == u"TODO"


def contains_active_date(heading):
	u"""
	Return True if heading contains an active date.
	"""
	return not(heading.active_date is None)

# vim: set noexpandtab:
