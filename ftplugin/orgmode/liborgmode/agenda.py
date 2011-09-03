# -*- coding: utf-8 -*-

"""
    Agenda
    ~~~~~~~~~~~~~~~~~~

    The agenda is one of the main concepts of orgmode.
    TODO

	* filtering
	* sorting
"""

from orgmode.liborgmode.agendafilter import *


class AgendaManager(object):
	"""Simple parsing of Documents to create an agenda."""
	def __init__(self):
		super(AgendaManager, self).__init__()
		self.agenda = []

	def get_todo(self, document):
		"""
		Get the todo agenda.
		"""
		# empty agenda
		self.agenda[:] = []
		# filter and return headings
		filtered = filter_items(document.all_headings(), [contains_active_todo])
		return sorted(filtered)

	def get_next_week_and_active_todo(self, document):
		"""
		Get the agenda for next week.
		"""
		# empty agenda
		self.agenda[:] = []
		# filter and return headings
		filtered = filter_items(document.all_headings(),
				[is_within_week_and_active_todo])
		return sorted(filtered)


# vim: set noexpandtab:
