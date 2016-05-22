# -*- coding: utf-8 -*-

u"""
	Agenda
	~~~~~~~~~~~~~~~~~~

	The agenda is one of the main concepts of orgmode. It allows to
	collect TODO items from multiple org documents in an agenda view.

	Features:
	* filtering
	* sorting
"""

from orgmode.liborgmode.agendafilter import filter_items
from orgmode.liborgmode.agendafilter import is_within_week_and_active_todo
from orgmode.liborgmode.agendafilter import contains_active_todo
from orgmode.liborgmode.agendafilter import contains_active_date


class AgendaManager(object):
	u"""Simple parsing of Documents to create an agenda."""
	# TODO Move filters in this file, they do the same thing

	def __init__(self):
		super(AgendaManager, self).__init__()

	def get_todo(self, documents):
		u"""
		Get the todo agenda for the given documents (list of document).
		"""
		filtered = []
		for document in iter(documents):
			# filter and return headings
			filtered.extend(filter_items(document.all_headings(),
								[contains_active_todo]))
		return sorted(filtered)

	def get_next_week_and_active_todo(self, documents):
		u"""
		Get the agenda for next week for the given documents (list of
		document).
		"""
		filtered = []
		for document in iter(documents):
			# filter and return headings
			filtered.extend(filter_items(document.all_headings(),
								[is_within_week_and_active_todo]))
		return sorted(filtered)

	def get_timestamped_items(self, documents):
		u"""
		Get all time-stamped items in a time-sorted way for the given
		documents (list of document).
		"""
		filtered = []
		for document in iter(documents):
			# filter and return headings
			filtered.extend(filter_items(document.all_headings(),
								[contains_active_date]))
		return sorted(filtered)

# vim: set noexpandtab:
