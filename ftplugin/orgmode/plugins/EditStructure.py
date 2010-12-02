from orgmode import echo, echom, echoe, ORGMODE
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
		self.menu = ORGMODE.orgmenu + Submenu('&Edit Structure')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	#def _action_heading(self, action, heading):
	#	if not heading:
	#		echom('Heading not found.')
	#		return

	#	if action not in ('y', 'd'):
	#		echoe('Action not in  y(ank) or d(elete).')
	#		return

	#	end = '$'
	#	h = heading
	#	while h:
	#		if h.next_sibling:
	#			end = h.next_sibling.start
	#			break
	#		elif h.level == 1:
	#			break
	#		elif h.parent:
	#			h = h.parent

	#	vim.command(':%s,%s%s' % (heading.start + 1, end, action))

	def new_heading(self, below=True):
		h = Heading.current_heading()
		if not h:
			if below:
				vim.eval('feedkeys("o", "n")')
			else:
				vim.eval('feedkeys("O", "n")')
			return

		if below:
			pos = h.end + 1
			level = h.level
			if h.children:
				level = h.children[0].level
		else:
			pos = h.start
			level = h.level
			if h.parent:
				if h.parent.children[0].start == h.start:
					level = h.parent.level + 1

		tmp = ['%s ' % ('*' * level)] + vim.current.buffer[pos:]
		del vim.current.buffer[pos:]
		vim.current.buffer.append(tmp)
		vim.command('normal %dggA' % (pos + 1, ))

		# not sure what to return here .. line number of new heading or old heading object?
		return h

	def new_heading_below(self):
		return self.new_heading(True)

	def new_heading_above(self):
		return self.new_heading(False)

	#def copy_heading(self):
	#	self._action_heading('y', Heading.current_heading())

	#def delete_heading(self):
	#	self._action_heading('d', Heading.current_heading())

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.menu + ActionEntry('New Heading &below', Keybinding('o', ':py ORGMODE.plugins["EditStructure"].new_heading_below()<CR>'))
		self.menu + ActionEntry('New Heading &above', Keybinding('O', ':py ORGMODE.plugins["EditStructure"].new_heading_above()<CR>'))
		#self.menu + ActionEntry('Copy/yank Subtree', Keybinding('y}', ':py ORGMODE.plugins["EditStructure"].copy_heading()<CR>'))
		#self.menu + ActionEntry('Delete Subtree', Keybinding('d}', ':py ORGMODE.plugins["EditStructure"].delete_heading()<CR>'))
