# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, apply_count, repeat, realign_tags
from orgmode.menu import Submenu, ActionEntry
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug
from liborgmode import Document, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim


class Todo(object):
	"""
	Todo plugin.

	Description taken from orgmode.org:

	You can use TODO keywords to indicate different sequential states in the
	process of working on an item, for example:

	["TODO", "FEEDBACK", "VERIFY", "|", "DONE", "DELEGATED"]

	The vertical bar separates the TODO keywords (states that need action) from
	the DONE states (which need no further action). If you don't provide the
	separator bar, the last state is used as the DONE state. With this setup,
	the command ``,d`` will cycle an entry from TODO to FEEDBACK, then to
	VERIFY, and finally to DONE and DELEGATED.
	"""

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('&TODO Lists')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def _get_states(cls):
		"""
		Return the next states divided in TODO states and DONE states.
		"""
		states = settings.get('org_todo_keywords', [])
		if not '|' in states:
			return states[:-1], [states[-1]]
		else:
			seperator_pos = states.index('|')
			return states[0:seperator_pos], states[seperator_pos + 1:]

	@classmethod
	def _get_next_state(cls, current_state, all_states,
			direction=DIRECTION_FORWARD):
		"""
		Return the next state as string, or NONE if the next state is no state.
		"""
		if not current_state in all_states:
			if direction == DIRECTION_FORWARD:
				return all_states[0]
			else:
				return all_states[-1]
		else:
			current_pos = all_states.index(current_state)
			if direction == DIRECTION_FORWARD:
				next_pos = current_pos + 1
			else:
				next_pos = current_pos - 1

			if next_pos < 0 or next_pos >= len(all_states):
				return None
			return all_states[next_pos]

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def toggle_todo_state(cls, direction=DIRECTION_FORWARD):
		""" Toggle state of TODO item

		:returns: The changed heading
		"""
		d = ORGMODE.get_document()
		lineno, colno = vim.current.window.cursor

		# get heading
		heading = d.current_heading()
		if not heading:
			vim.eval('feedkeys("^", "n")')
			return

		# get todo states
		todo_states, done_states = Todo._get_states()
		all_states = todo_states + done_states
		if len(all_states) < 2:
			echom('No todo keywords configured.')
			return

		# current_state
		current_state = heading.todo

		# get new state
		new_state = Todo._get_next_state(current_state, all_states, direction)

		# set new headline
		heading.todo = new_state

		# move cursor along with the inserted state only when current position
		# is in the heading; otherwite do nothing
		if heading.start_vim == lineno:
			if current_state is None:
				offset = len(new_state)
			elif new_state is None:
				offset = -len(current_state)
			else:
				offset = len(current_state) - len(new_state)
			vim.current.window.cursor = (lineno, colno + offset)

		# plug
		plug = 'OrgToggleTodoForward'
		if direction == DIRECTION_BACKWARD:
			plug = 'OrgToggleTodoBackward'

		d.write()

		return plug

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		settings.set('org_leader', ',')
		leader = settings.get('org_leader', ',')

		self.keybindings.append(Keybinding('%sd' % leader, Plug(
			'OrgToggleTodoToggle',
			':silent! py ORGMODE.plugins["Todo"].toggle_todo_state()<CR>')))
		self.menu + ActionEntry('&TODO/DONE/-', self.keybindings[-1])
		submenu = self.menu + Submenu('Select &keyword')
		self.keybindings.append(Keybinding('<S-Right>', Plug(
			'OrgToggleTodoForward',
			':silent! py ORGMODE.plugins["Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry('&Next keyword', self.keybindings[-1])
		self.keybindings.append(Keybinding('<S-Left>', Plug(
			'OrgToggleTodoBackward',
			':silent! py ORGMODE.plugins["Todo"].toggle_todo_state(False)<CR>')))
		submenu + ActionEntry('&Previous keyword', self.keybindings[-1])

		settings.set('org_todo_keywords', ['TODO', '|', 'DONE'])

# vim: set noexpandtab:
