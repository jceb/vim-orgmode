from orgmode import echo, ORGMODE, apply_count
from orgmode.menu import Submenu, HorizontalLine, ActionEntry
from orgmode.keybinding import Keybinding, MODE_VISUAL, MODE_ALL, MODE_NORMAL
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class Navigator(object):
	""" Implement navigation in org-mode documents """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + Submenu('&Navigate Headings')
		self.keybindings = []

	@apply_count
	def parent(self, visualmode=False):
		"""
		Focus parent heading

		:returns: parent heading or None
		"""
		heading = Heading.current_heading()
		if not heading:
			echo('No heading found')
			return

		if not heading.parent:
			echo('No parent heading found')
			return

		if visualmode:
			self._change_visual_selection(heading.parent, direction=DIRECTION_BACKWARD)
		else:
			vim.current.window.cursor = (heading.parent.start + 1, heading.parent.level + 2)
		return heading.parent


	def _change_visual_selection(self, heading, direction=DIRECTION_FORWARD, noheadingfound=False):
		visualmode = vim.eval('visualmode()')
		current = vim.current.window.cursor[0]
		line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
		line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]

		f_start = heading.start + 1
		f_end = heading.end + 1
		swap_cursor = True

		# |visual start <- cursor position: |
		# selection end
		if current == line_start:
			if (direction == DIRECTION_FORWARD and line_end < f_start) or noheadingfound:
				swap_cursor = False

			# focus heading HERE
			# |visual start <- cursor position: |
			# selection end

			# |visual start <- cursor position: |
			# focus heading HERE
			# selection end
			if (f_start < line_start or f_start < line_end) and not noheadingfound:
				line_start = f_start

			# |visual start <- cursor position: |
			# selection end
			# focus heading HERE
			else:
				line_start = line_end
				line_end = f_end

		# visual start <- cursor position: |
		# selection end|
		else:
			# focus heading HERE
			# visual start <- cursor position: |
			# selection end|
			if f_start < line_start:
				line_end = line_start
				line_start = f_start

			# visual start <- cursor position: |
			# selection end and focus heading end HERE|

			# visual start <- cursor position: |
			# focus heading HERE
			# selection end|

			# visual start <- cursor position: |
			# selection end|
			# focus heading HERE
			else:
				if direction == DIRECTION_FORWARD:
					if current < f_start - 1:
						# focus end of previous heading instead of beginning of next heading
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_end = f_end
				else:
					line_end = f_start
				swap_cursor = False

		move_col_start = '%dl' % (col_start - 1) if (col_start - 1) else ''
		move_col_end = '%dl' % (col_end - 1) if (col_end - 1) else ''
		swap = 'o' if swap_cursor else ''

		vim.command('normal %dgg%s%s%dgg%s%s' % \
				(line_start, move_col_start, visualmode, line_end, move_col_end, swap))

	def _focus_heading(self, direction=DIRECTION_FORWARD, visualmode=False):
		"""
		Focus next or previous heading in the given direction

		:direction: True for next heading, False for previous heading
		:returns: next heading or None
		"""
		heading = Heading.current_heading()
		focus_heading = None
		if not heading:
			if direction == DIRECTION_FORWARD:
				focus_heading = Heading.next_heading(ORGMODE.mode)
			if not (heading or focus_heading):
				echo('No heading found')
				return
		if direction == DIRECTION_BACKWARD:
			if vim.current.window.cursor[0] - 1 != heading.start:
				focus_heading = heading

		if not focus_heading:
			if direction == DIRECTION_FORWARD and heading.children:
				focus_heading = heading.children[0]
			elif direction == DIRECTION_FORWARD and heading.next_sibling:
				focus_heading = heading.next_sibling
			elif direction == DIRECTION_BACKWARD and heading.previous_sibling:
				focus_heading = heading.previous_sibling
				while focus_heading.children:
					focus_heading = focus_heading.children[-1]
			else:
				while heading.level > 1:
					if heading.parent:
						if direction == DIRECTION_FORWARD and heading.parent.next_sibling:
							focus_heading = heading.parent.next_sibling
							break
						elif direction == DIRECTION_BACKWARD:
							focus_heading = heading.parent
							break
						else:
							heading = heading.parent
					else:
						break

		noheadingfound = False
		if not focus_heading:
			if visualmode:
				# the cursor seems to be on the last heading of this document
				# and performes another next-operation
				focus_heading = heading
				noheadingfound = True
			else:
				if direction == DIRECTION_FORWARD:
					echo('Already focussing last heading')
				else:
					echo('Already focussing first heading')
				return

		if visualmode:
			self._change_visual_selection(focus_heading, direction=direction, noheadingfound=noheadingfound)
		else:
			vim.current.window.cursor = (focus_heading.start + 1, focus_heading.level + 2)
		if noheadingfound:
			return
		return focus_heading

	@apply_count
	def previous(self, visualmode=None):
		"""
		Focus previous heading
		"""
		return self._focus_heading(direction=DIRECTION_BACKWARD, visualmode=visualmode)

	@apply_count
	def next(self, visualmode=None):
		"""
		Focus next heading
		"""
		return self._focus_heading(direction=DIRECTION_FORWARD, visualmode=visualmode)

	@apply_count
	def previous_end(self, indent=None, visualmode=None):
		"""
		Focus end of (next) heading
		"""
		return self._focus_heading(direction=DIRECTION_BACKWARD, visualmode=visualmode)

	@apply_count
	def next_end(self, indent=None, visualmode=None):
		"""
		Focus end of (next) heading
		"""
		return self._focus_heading(direction=DIRECTION_FORWARD, visualmode=visualmode)

	def register(self):
		self.menu + ActionEntry('Up', Keybinding('g{', ':py ORGMODE.plugins["Navigator"].parent()<CR>'))
		self.menu + ActionEntry('Previous', Keybinding('{', ':py ORGMODE.plugins["Navigator"].previous()<CR>'))
		self.menu + ActionEntry('Next', Keybinding('}', ':py ORGMODE.plugins["Navigator"].next()<CR>'))
		self.keybindings.append(Keybinding('g{', '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].parent(visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding('{', '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].previous(visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding('}', '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].next(visualmode=True)"<CR>', mode=MODE_VISUAL))

		self.keybindings.append(Keybinding("`{", ':py ORGMODE.plugins[\'Navigator\'].previous_end(indent=True)<CR>', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding("'{", ':py ORGMODE.plugins[\'Navigator\'].previous_end(indent=False)<CR>', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding("`}", ':py ORGMODE.plugins[\'Navigator\'].next_end(indent=True)<CR>', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding("'}", ':py ORGMODE.plugins[\'Navigator\'].next_end(indent=False)<CR>', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding("`{", '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].previous_end(indent=True, visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding("'{", '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].previous_end(indent=False, visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding("`}", '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].next_end(indent=True, visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding("'}", '<Esc>:<C-u>exe "py ORGMODE.plugins[\'Navigator\'].next_end(indent=False, visualmode=True)"<CR>', mode=MODE_VISUAL))
