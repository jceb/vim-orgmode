# -*- coding: utf-8 -*-

"""
    Agenda
    ~~~~~~~~~~~~~~~~~~

    The agenda is one of the main concepts of orgmode.
    TODO

	* filtering
	* sorting
"""

class AgendaManager(object):
	"""Simple parsing of Documents to create an agenda."""
	def __init__(self):
		super(AgendaManager, self).__init__()
		self.agenda = []

	def get_agenda_todo(self, document):
		"""
		Get the todo agenda.
		"""
		# empty agenda
		self.agenda[:] = []
		# setup todo filter
		self.all_criteria = [self.criteria_todo]
		# filter and return headings
		return filter(self.meets_criteria, document.all_headings())

	def get_agenda(self, document, criteria=None):
		""""
		Get an agenda.
		"""
		self.document = document
		self.active_todo_states = document.get_todo_states()[0]

		# empty agenda
		self.agenda[:] = []

		# setup filter
		self.all_criteria = [
				self.criteria_active_todo,
				self.criteria_active_date
				]
		# filter headings
		return filter(self.meets_criteria, document.all_headings())


	def meets_criteria(self, heading):
		for fn in self.all_criteria:
			if fn(heading):
				return True
		return False

	def criteria_active_todo(self, heading):
		"""
		Return True if heading contains an active TODO.
		"""
		TODO, DONE = self.active_todo_states
		return heading.todo == "TODO"

	def criteria_active_date(self, heading):
		"""
		Return True if heading contains an active date.
		"""
		return not heading.active_date is None

# vim: set noexpandtab:
