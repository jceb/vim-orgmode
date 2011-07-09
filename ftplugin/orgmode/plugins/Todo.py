# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, apply_count, repeat, realign_tags, DIRECTION_FORWARD, DIRECTION_BACKWARD
from orgmode.menu import Submenu, ActionEntry
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug

import vim


class Todo(object):
	u"""
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
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&TODO Lists')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def _get_next_state(cls, current_state, all_states,
			direction=DIRECTION_FORWARD, interactive=False, next_set=False):
		u"""
		:current_state:		the current todo state
		:all_states:		a list containing all todo states within sublists.
							The todo states may contain access keys
		:direction:			direction of state or keyword set change (forward/backward)
		:interactive:		if interactive and more than one todo sequence is
							specified, open a selection window
		:next_set:			advance to the next keyword set in defined direction

		:return:			return the next state as string, or NONE if the
							next state is no state.
		"""
		if not all_states:
			return

		def split_access_key(t):
			u"""
			:t:		todo state

			:return:	todo state and access key separated (TODO, ACCESS_KEY)
			"""
			idx = t.find(u'(')
			t, k = (t[:idx], t[idx + 1:-1] if t[idx + 1:-1] else None) if idx != -1 else (t, None)
			return (t, k)

		def find_current_todo_state(c, a, stop=0):
			u"""
			:c:		current todo state
			:a:		list of todo states
			:stop:	internal parameter for parsing only two levels of lists

			:return:	first position of todo state in list in the form
						(IDX_TOPLEVEL, IDX_SECOND_LEVEL (0|1), IDX_OF_ITEM)
			"""
			for i in xrange(0, len(a)):
				if type(a[i]) in (tuple, list) and stop < 2:
					r = find_current_todo_state(c, a[i], stop=stop + 1)
					if r:
						r.insert(0, i)
						return r
				# ensure that only on the second level of sublists todo states
				# are found
				if type(a[i]) == unicode and stop == 2:
					_i = split_access_key(a[i])[0]
					if c == _i:
						return [i]

		if not interactive:
			ci = find_current_todo_state(current_state, all_states)

			if not ci:
				if next_set and direction == DIRECTION_BACKWARD:
					echom(u'Already at the first keyword set')
					return current_state

				return split_access_key(all_states[0][0][0] if all_states[0][0] else all_states[0][1][0])[0] \
						if direction == DIRECTION_FORWARD else \
						split_access_key(all_states[0][1][-1] if all_states[0][1] else all_states[0][0][-1])[0]
			elif next_set:
				if direction == DIRECTION_FORWARD and ci[0] + 1 < len(all_states[ci[0]]):
					echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] + 1][0]), u', '.join(all_states[ci[0] + 1][1])))
					return split_access_key(all_states[ci[0] + 1][0][0] \
							if all_states[ci[0] + 1][0] else all_states[ci[0] + 1][1][0])[0]
				elif current_state is not None and direction == DIRECTION_BACKWARD and ci[0] - 1 >= 0:
					echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] - 1][0]), u', '.join(all_states[ci[0] - 1][1])))
					return split_access_key(all_states[ci[0] - 1][0][0] \
							if all_states[ci[0] - 1][0] else all_states[ci[0] - 1][1][0])[0]
				else:
					echom(u'Already at the %s keyword set' % (u'first' if direction == DIRECTION_BACKWARD else u'last'))
					return current_state
			else:
				next_pos = ci[2] + 1 if direction == DIRECTION_FORWARD else ci[2] - 1
				if direction == DIRECTION_FORWARD:
					if next_pos < len(all_states[ci[0]][ci[1]]):
						# select next state within done or todo states
						return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

					elif not ci[1] and next_pos - len(all_states[ci[0]][ci[1]]) < len(all_states[ci[0]][ci[1] + 1]):
						# finished todo states, jump to done states
						return split_access_key(all_states[ci[0]][ci[1] + 1][next_pos - len(all_states[ci[0]][ci[1]])])[0]
				else:
					if next_pos >= 0:
						# select previous state within done or todo states
						return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

					elif ci[1] and len(all_states[ci[0]][ci[1] - 1]) + next_pos < len(all_states[ci[0]][ci[1] - 1]):
						# finished done states, jump to todo states
						return split_access_key(all_states[ci[0]][ci[1] - 1][len(all_states[ci[0]][ci[1] - 1]) + next_pos])[0]
		else:
			# create new window
			# make window a scratch window, leaving the window is not possible!
			# map access keys to callback that updates current heading
			# map selection keys
			pass

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def toggle_todo_state(cls, direction=DIRECTION_FORWARD, interactive=False, next_set=False):
		u""" Toggle state of TODO item

		:returns: The changed heading
		"""
		d = ORGMODE.get_document(allow_dirty=True)
		lineno, colno = vim.current.window.cursor

		# get heading
		heading = d.find_current_heading()
		if not heading:
			vim.eval(u'feedkeys("^", "n")')
			return

		todo_states = d.get_todo_states(strip_access_key=False)
		# get todo states
		if not todo_states:
			echom(u'No todo keywords configured.')
			return

		# current_state
		current_state = heading.todo

		# get new state
		new_state = Todo._get_next_state(current_state, todo_states, \
				direction=direction, interactive=interactive, next_set=next_set)

		# move cursor along with the inserted state only when current position
		# is in the heading; otherwite do nothing
		if heading.start_vim == lineno:
			if current_state is None and new_state is None:
				offset = 0
			elif current_state is None:
				offset = len(new_state)
			elif new_state is None:
				offset = -len(current_state)
			else:
				offset = len(current_state) - len(new_state)
			vim.current.window.cursor = (lineno, colno + offset)

		# set new headline
		heading.todo = new_state

		# plug
		plug = u'OrgTodoForward'
		if direction == DIRECTION_BACKWARD:
			plug = u'OrgTodoBackward'

		d.write_heading(heading)

		return plug

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%sd' % leader, Plug(
			u'OrgTodoToggle',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=True)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/-', self.keybindings[-1])
		submenu = self.menu + Submenu(u'Select &keyword')

		self.keybindings.append(Keybinding(u'<S-Right>', Plug(
			u'OrgTodoForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry(u'&Next keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Left>', Plug(
			u'OrgTodoBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=False)<CR>')))
		submenu + ActionEntry(u'&Previous keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Right>', Plug(
			u'OrgTodoSetForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(next_set=True)<CR>')))
		submenu + ActionEntry(u'Next keyword &set', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Left>', Plug(
			u'OrgTodoSetBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=False, next_set=True)<CR>')))
		submenu + ActionEntry(u'Previous &keyword set', self.keybindings[-1])

		settings.set(u'org_todo_keywords', [u'TODO'.encode(u'utf-8'), u'|'.encode(u'utf-8'), u'DONE'.encode(u'utf-8')])

# vim: set noexpandtab:
