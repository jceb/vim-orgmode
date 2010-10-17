from orgmode import echo, ORGMODE
from orgmode.menu import Submenu, HorizontalLine, ActionEntry
from orgmode.keybinding import Keybinding
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class EditStructure(object):
	""" EditStructure plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('EditStructure')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	def _action_heading(self, action, heading):
		if not heading:
			echom('Heading not found.')
			return

		if action not in ('y', 'd'):
			echoerr('Action not in  y(ank) or d(elete).')
			return

		end = '$'
		h = heading
		while h:
			if h.next_sibling:
				end = h.next_sibling.start
				break
			elif h.level == 1:
				break
			elif h.parent:
				h = h.parent

		vim.command(':%s,%s%s' % (heading.start + 1, end, action))

	def copy_heading(self):
		self._action_heading('y', Heading.current_heading())

	def delete_heading(self):
		self._action_heading('d', Heading.current_heading())

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.menu + ActionEntry('Copy/yank Subtree', Keybinding('y}', ':py ORGMODE.plugins["EditStructure"].copy_heading()<CR>'))
		self.menu + ActionEntry('Delete Subtree', Keybinding('d}', ':py ORGMODE.plugins["EditStructure"].delete_heading()<CR>'))
