from orgmode import echo, echom, echoe, ORGMODE, apply_count, MODE_STAR, MODE_INDENT
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

	def new_heading(self, below=True, mode=MODE_STAR):
		h = Heading.current_heading(mode=mode)
		if not h or h.start + 1 != vim.current.window.cursor[0]:
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

		leading_char = '*' if mode == MODE_STAR else ' '

		tmp = ['%s* ' % (leading_char * (level - 1)), ''] + vim.current.buffer[pos:]
		del vim.current.buffer[pos:]
		vim.current.buffer.append(tmp)
		vim.command('exe "normal %dgg"|startinsert!' % (pos + 1, ))

		# not sure what to return here .. line number of new heading or old heading object?
		return h

	def new_heading_below(self, mode=MODE_STAR):
		return self.new_heading(True, mode=mode)

	def new_heading_above(self, mode=MODE_STAR):
		return self.new_heading(False, mode=mode)

	def _change_heading_level(self, level, relative=True, mode=MODE_STAR):
		h = Heading.current_heading(mode=mode)
		if not h or h.start + 1 != vim.current.window.cursor[0]:
			if (relative and level > 0) or (not relative and level > h.level):
				vim.eval('feedkeys(">>", "n")')
			else:
				vim.eval('feedkeys("<<", "n")')
			# return True because otherwise apply_count will not work
			return True

		# don't allow demotion below level 1
		if h.level == 1 and level < 1:
			return False

		# reduce level of demotion to a minimum heading level of 1
		if (h.level + level) < 1:
			level = h.level - 1

		leading_char = '*' if mode == MODE_STAR else ' '

		def indent(heading, _buffer):
			if not heading:
				return _buffer
			# strip level and add new level
			_buffer[heading.start] = '%s*%s' % (leading_char * (heading.level + level - 1), _buffer[heading.start][heading.level:])

			for child in heading.children:
				_buffer = indent(child, _buffer)
			return _buffer

		# save cursor position
		c = vim.current.window.cursor[:]
		eolc = h.end_of_last_child
		vim_buffer = vim.current.buffer[:]
		vim_buffer = indent(h, vim_buffer)
		del vim.current.buffer[h.start:]
		vim.current.buffer.append(vim_buffer[h.start:])
		# indent the promoted/demoted heading
		vim.command('normal %dggV%dgg=' % (h.start + 1, eolc + 1))
		# restore cursor position
		vim.current.window.cursor = (c[0], c[1] + level)

		return True

	@apply_count
	def demote_heading(self, mode=MODE_STAR):
		return self._change_heading_level(-1, mode=mode)

	@apply_count
	def promote_heading(self, mode=MODE_STAR):
		return self._change_heading_level(1, mode=mode)

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
		self.menu + ActionEntry('&Promote Heading', Keybinding('>>', ':py ORGMODE.plugins["EditStructure"].promote_heading()<CR>'))
		self.menu + ActionEntry('&Demote Heading', Keybinding('<<', ':py ORGMODE.plugins["EditStructure"].demote_heading()<CR>'))
		#self.menu + ActionEntry('Copy/yank Subtree', Keybinding('y}', ':py ORGMODE.plugins["EditStructure"].copy_heading()<CR>'))
		#self.menu + ActionEntry('Delete Subtree', Keybinding('d}', ':py ORGMODE.plugins["EditStructure"].delete_heading()<CR>'))
