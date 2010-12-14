from orgmode import echo, echom, echoe, ORGMODE, apply_count
from orgmode.menu import Submenu, HorizontalLine, ActionEntry
from orgmode.keybinding import Keybinding
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

	@apply_count
	def toggle_todo_state(self):
		""" Toggle state of TODO item

		:returns: The changed heading
	    """
		heading = Heading.current_heading()
		if not heading or vim.current.window.cursor[0] != heading.start_vim:
			vim.eval('feedkeys("^", "n")')
			return

		# TODO: externalize states to a settings plugin and make them customizable
		states = ('TODO', 'NEXT', 'STARTED', 'DONE', 'CANCELED', '')

		current_state, rest = heading.text.split(' ', 1)
		new_state = states[0]
		if current_state in states:
			# advance to next state
			new_state = states[(states.index(current_state) + 1) % len(states)]
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

		return heading

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		self.menu + ActionEntry('&TODO/DONE/-', Keybinding('^', ':py ORGMODE.plugins["Todo"].toggle_todo_state()<CR>'))
		#self.keybindings.append(Keybinding("keybinding", ':action'))
