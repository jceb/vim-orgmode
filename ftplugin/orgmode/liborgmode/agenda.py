# -*- coding: utf-8 -*-

u"""
    Agenda
    ~~~~~~~~~~~~~~~~~~

    The agenda is one of the main concepts of orgmode.
    TODO

	* filtering
	* sorting
"""

from orgmode.liborgmode.agendafilter import *


class AgendaManager(object):
	u"""Simple parsing of Documents to create an agenda."""

	def __init__(self):
		super(AgendaManager, self).__init__()

	def get_todo(self, documents):
		u"""
		Get the todo agenda for the given documents (list of document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(), [contains_active_todo])
			filtered.extend(tmp)
		return sorted(filtered)

	def get_next_week_and_active_todo(self, documents):
		u"""
		Get the agenda for next week for the given documents (list of
		document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(),
				[is_within_week_and_active_todo])
			filtered.extend(tmp)
		return sorted(filtered)

	def get_timestamped_items(self, documents):
		u"""
		Get all time-stamped items in a time-sorted way for the given
		documents (list of document).
		"""
		filtered = []
		for i, document in enumerate(documents):
			# filter and return headings
			tmp = filter_items(document.all_headings(),
				[contains_active_date])
			filtered.extend(tmp)
		return sorted(filtered)

# vim: set noexpandtab:
