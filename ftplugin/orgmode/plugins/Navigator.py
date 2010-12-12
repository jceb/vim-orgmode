# -*- coding: utf-8 -*-

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
			if visualmode:
				vim.command('normal gv')
			else:
				echo('No heading found')
			return

		if not heading.parent:
			if visualmode:
				vim.command('normal gv')
			else:
				echo('No parent heading found')
			return

		if visualmode:
			self._change_visual_selection(heading, heading.parent, direction=DIRECTION_BACKWARD, parent=True)
		else:
			vim.current.window.cursor = (heading.parent.start_vim, heading.parent.level + 1)
		return heading.parent


	def _change_visual_selection(self, current_heading, heading, direction=DIRECTION_FORWARD, noheadingfound=False, parent=False):
		visualmode = vim.eval('visualmode()')
		current = vim.current.window.cursor[0]
		line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
		line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]

		f_start = heading.start_vim
		f_end = heading.end_vim
		swap_cursor = True

		# << |visual start
		# selection end >>
		if current == line_start:
			if (direction == DIRECTION_FORWARD and line_end < f_start) or noheadingfound and not direction == DIRECTION_BACKWARD:
				swap_cursor = False

			# focus heading HERE
			# << |visual start
			# selection end >>

			# << |visual start
			# focus heading HERE
			# selection end >>
			if f_start < line_start and direction == DIRECTION_BACKWARD:
				if current_heading.start_vim < line_start and not parent:
					line_start = current_heading.start_vim
				else:
					line_start = f_start

			elif (f_start < line_start or f_start < line_end) and not noheadingfound:
				line_start = f_start

			# << |visual start
			# selection end >>
			# focus heading HERE
			else:
				if direction == DIRECTION_FORWARD:
					if line_end < f_start and not line_start == f_start - 1 and current_heading:
						# focus end of previous heading instead of beginning of next heading
						line_start = line_end
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_start = line_end
						line_end = f_end
				elif direction == DIRECTION_BACKWARD:
					if line_end < f_end:
						pass
				else:
					line_start = line_end
					line_end = f_end

		# << visual start
		# selection end| >>
		else:
			# focus heading HERE
			# << visual start
			# selection end| >>
			if line_start > f_start and line_end > f_end and not parent:
				line_end = f_end
				swap_cursor = False

			elif line_start > f_start or \
					line_start == f_start and line_end <= f_end and direction == DIRECTION_BACKWARD:
				line_end = line_start
				line_start = f_start

			# << visual start
			# selection end and focus heading end HERE| >>

			# << visual start
			# focus heading HERE
			# selection end| >>

			# << visual start
			# selection end| >>
			# focus heading HERE
			else:
				if direction == DIRECTION_FORWARD:
					if line_end < f_start - 1:
						# focus end of previous heading instead of beginning of next heading
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_end = f_end
				else:
					line_end = f_end
				swap_cursor = False

		move_col_start = '%dl' % (col_start - 1) if (col_start - 1) > 0 and (col_start - 1) < 2000000000 else ''
		move_col_end = '%dl' % (col_end - 1) if (col_end - 1) > 0 and (col_end - 1) < 2000000000 else ''
		swap = 'o' if swap_cursor else ''

		vim.command('normal %dgg%s%s%dgg%s%s' % \
				(line_start, move_col_start, visualmode, line_end, move_col_end, swap))

	def _focus_heading(self, direction=DIRECTION_FORWARD, visualmode=False):
		"""
		Focus next or previous heading in the given direction

		:direction: True for next heading, False for previous heading
		:returns: next heading or None
		"""
		current_heading = Heading.current_heading()
		heading = current_heading
		focus_heading = None
		if not heading:
			if direction == DIRECTION_FORWARD:
				focus_heading = Heading.next_heading(ORGMODE.mode)
			if not (heading or focus_heading):
				if visualmode:
					# restore visual selection when no heading was found
					vim.command('normal gv')
				else:
					echo('No heading found')
				return
		#elif direction == DIRECTION_BACKWARD and not visualmode:
		elif direction == DIRECTION_BACKWARD:
			if vim.current.window.cursor[0] != heading.start_vim:
				if visualmode:
					line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
					line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]
					if line_start >= heading.start_vim and line_end > heading.start_vim:
						focus_heading = heading
				else:
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
				# the cursor seems to be on the last or first heading of this
				# document and performes another next/previous-operation
				focus_heading = heading
				noheadingfound = True
			else:
				if direction == DIRECTION_FORWARD:
					echo('Already focussing last heading')
				else:
					echo('Already focussing first heading')
				return

		if visualmode:
			self._change_visual_selection(current_heading, focus_heading, direction=direction, noheadingfound=noheadingfound)
		else:
			vim.current.window.cursor = (focus_heading.start_vim, focus_heading.level + 1)
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
		self.menu + ActionEntry('&Up', Keybinding('g{', ':py ORGMODE.plugins["Navigator"].parent()<CR>'))
		self.menu + ActionEntry('&Previous', Keybinding('{', ':py ORGMODE.plugins["Navigator"].previous()<CR>'))
		self.menu + ActionEntry('&Next', Keybinding('}', ':py ORGMODE.plugins["Navigator"].next()<CR>'))
		self.keybindings.append(Keybinding('g{', '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].parent(visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding('{', '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].previous(visualmode=True)"<CR>', mode=MODE_VISUAL))
		self.keybindings.append(Keybinding('}', '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].next(visualmode=True)"<CR>', mode=MODE_VISUAL))

		#self.keybindings.append(Keybinding("`{", ':py ORGMODE.plugins["Navigator"].previous_end(indent=True)<CR>', mode=MODE_NORMAL))
		#self.keybindings.append(Keybinding("'{", ':py ORGMODE.plugins["Navigator"].previous_end(indent=False)<CR>', mode=MODE_NORMAL))
		#self.keybindings.append(Keybinding("`}", ':py ORGMODE.plugins["Navigator"].next_end(indent=True)<CR>', mode=MODE_NORMAL))
		#self.keybindings.append(Keybinding("'}", ':py ORGMODE.plugins["Navigator"].next_end(indent=False)<CR>', mode=MODE_NORMAL))

		#self.keybindings.append(Keybinding("`{", '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].previous_end(indent=True, visualmode=True)"<CR>', mode=MODE_VISUAL))
		#self.keybindings.append(Keybinding("'{", '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].previous_end(indent=False, visualmode=True)"<CR>', mode=MODE_VISUAL))
		#self.keybindings.append(Keybinding("`}", '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].next_end(indent=True, visualmode=True)"<CR>', mode=MODE_VISUAL))
		#self.keybindings.append(Keybinding("'}", '<Esc>:<C-u>exe "py ORGMODE.plugins["Navigator"].next_end(indent=False, visualmode=True)"<CR>', mode=MODE_VISUAL))
