# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class Todo(object):
	""" Todo plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('&TODO Lists')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@repeat
	@apply_count
	def toggle_todo_state(self, direction=DIRECTION_FORWARD):
		""" Toggle state of TODO item

		:returns: The changed heading
	    """
		heading = Heading.current_heading()
		if not heading or vim.current.window.cursor[0] != heading.start_vim:
			vim.eval('feedkeys("^", "n")')
			return

		states = settings.get('org_todo_keywords', [])

		current_state = ''
		rest = ''
		if heading.text.find(' ') != -1:
			current_state, rest = heading.text.split(' ', 1)
		else:
			rest = heading.text

		action_states = []
		done_states = []

		if states and isinstance(states[0], list):
			found_list = False
			for state_list in states:
				if state_list and current_state in state_list or not current_state:
					states = state_list
					found_list = True
					break
			if not found_list:
				states = states[0]

		if '|' not in states:
			action_states = states
		else:
			state_sep = states.index('|')
			action_states = states[:state_sep]
			done_states = filter(lambda x: x != '|', states[state_sep + 1:])
			done_states.append('')

		states = action_states + done_states

		if len(states) < 2:
			echom('No todo keywords configured.')
			return

		new_state = states[0]
		if direction == DIRECTION_BACKWARD:
			new_state = states[-2]

		if current_state != '|' and current_state in states:
			# advance to next/previous state
			if direction == DIRECTION_FORWARD:
				new_state = states[(states.index(current_state) + 1) % len(states)]
			else:
				new_state = states[(states.index(current_state) + len(states) - 1) % len(states)]
		else:
			rest = ' '.join((current_state, rest))
			current_state = ''

		if not new_state:
			vim.current.buffer[heading.start] = ' '.join(('*' * heading.level, rest))
		else:
			vim.current.buffer[heading.start] = ' '.join(('*' * heading.level, new_state, rest))

		# move cursor along with the inserted state
		if vim.current.window.cursor[1] > (heading.level + len(current_state)):
			extra = 1 if not current_state else -1 if not new_state else 0
			vim.current.window.cursor = (vim.current.window.cursor[0], vim.current.window.cursor[1] + len(new_state) - len(current_state) + extra)
		elif vim.current.window.cursor[1] > heading.level:
			vim.current.window.cursor = (vim.current.window.cursor[0], heading.level)

		plug = 'OrgToggleTodoForward'
		if direction == DIRECTION_BACKWARD:
			plug = 'OrgToggleTodoBackward'

		return plug

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		settings.set('org_leader', ',')
		leader = settings.get('org_leader', ',')

		self.keybindings.append(Keybinding('%sd' % leader, Plug('OrgToggleTodoToggle', ':silent! py ORGMODE.plugins["Todo"].toggle_todo_state()<CR>')))
		self.menu + ActionEntry('&TODO/DONE/-', self.keybindings[-1])
		submenu = self.menu + Submenu('Select &keyword')
		self.keybindings.append(Keybinding('<S-Right>', Plug('OrgToggleTodoForward', ':silent! py ORGMODE.plugins["Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry('&Next keyword', self.keybindings[-1])
		self.keybindings.append(Keybinding('<S-Left>', Plug('OrgToggleTodoBackward', ':silent! py ORGMODE.plugins["Todo"].toggle_todo_state(False)<CR>')))
		submenu + ActionEntry('&Previous keyword', self.keybindings[-1])

		settings.set('org_todo_keywords', ['TODO', '|', 'DONE'])
