# -*- coding: utf-8 -*-

from orgmode import echo, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, MODE_VISUAL, MODE_OPERATOR, Plug
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class Navigator(object):
	""" Implement navigation in org-mode documents """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + Submenu('&Navigate Headings')
		self.keybindings = []

	@apply_count
	def parent(self, mode):
		"""
		Focus parent heading

		:returns: parent heading or None
		"""
		heading = Heading.current_heading()
		if not heading:
			if mode == 'visual':
				vim.command('normal gv')
			else:
				echo('No heading found')
			return

		if not heading.parent:
			if mode == 'visual':
				vim.command('normal gv')
			else:
				echo('No parent heading found')
			return

		if mode == 'visual':
			self._change_visual_selection(heading, heading.parent, mode, direction=DIRECTION_BACKWARD, parent=True)
		else:
			vim.current.window.cursor = (heading.parent.start_vim, heading.parent.level + 1)
		return heading.parent


	def _change_visual_selection(self, current_heading, heading, mode, direction=DIRECTION_FORWARD, noheadingfound=False, parent=False):
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
				(line_start, move_col_start, vim.eval('visualmode()'), line_end, move_col_end, swap))

	def _focus_heading(self, mode, direction=DIRECTION_FORWARD, skip_children=False):
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
				focus_heading = Heading.next_heading()
			if not (heading or focus_heading):
				if mode == 'visual':
					# restore visual selection when no heading was found
					vim.command('normal gv')
				else:
					echo('No heading found')
				return
		elif direction == DIRECTION_BACKWARD:
			if vim.current.window.cursor[0] != heading.start_vim:
				if mode == 'visual':
					# TODO maybe this has to be changed!
					line_start, col_start = [ int(i) for i in vim.eval('getpos("\'<")')[1:3] ]
					line_end, col_end = [ int(i) for i in vim.eval('getpos("\'>")')[1:3] ]
					if line_start >= heading.start_vim and line_end > heading.start_vim:
						focus_heading = heading
				else:
					focus_heading = heading

		if not focus_heading:
			if not skip_children and direction == DIRECTION_FORWARD and heading.children:
				focus_heading = heading.children[0]
			elif direction == DIRECTION_FORWARD and heading.next_sibling:
				focus_heading = heading.next_sibling
			elif direction == DIRECTION_BACKWARD and heading.previous_sibling:
				focus_heading = heading.previous_sibling
				if not skip_children:
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
			if mode in ('visual', 'operator'):
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

		if mode == 'visual':
			self._change_visual_selection(current_heading, focus_heading, mode, direction=direction, noheadingfound=noheadingfound)
		elif mode == 'operator':
			if direction == DIRECTION_FORWARD and vim.current.window.cursor[0] >= focus_heading.start_vim:
				vim.current.window.cursor = (focus_heading.end_vim, len(vim.current.buffer[focus_heading.end]))
			else:
				vim.current.window.cursor = (focus_heading.start_vim, 0)
		else:
			vim.current.window.cursor = (focus_heading.start_vim, focus_heading.level + 1)
		if noheadingfound:
			return
		return focus_heading

	@apply_count
	def previous(self, mode, skip_children=False):
		"""
		Focus previous heading
		"""
		return self._focus_heading(mode, direction=DIRECTION_BACKWARD, skip_children=skip_children)

	@apply_count
	def next(self, mode, skip_children=False):
		"""
		Focus next heading
		"""
		return self._focus_heading(mode, direction=DIRECTION_FORWARD, skip_children=skip_children)

	def register(self):
		# normal mode
		self.keybindings.append(Keybinding('g{', Plug('OrgJumpToParentNormal', ':py ORGMODE.plugins["Navigator"].parent(mode="normal")<CR>')))
		self.menu + ActionEntry('&Up', self.keybindings[-1])
		self.keybindings.append(Keybinding('{', Plug('OrgJumpToPreviousNormal', ':py ORGMODE.plugins["Navigator"].previous(mode="normal")<CR>')))
		self.menu + ActionEntry('&Previous', self.keybindings[-1])
		self.keybindings.append(Keybinding('}', Plug('OrgJumpToNextNormal', ':py ORGMODE.plugins["Navigator"].next(mode="normal")<CR>')))
		self.menu + ActionEntry('&Next', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding('g{', Plug('OrgJumpToParentVisual', '<Esc>:<C-u>py ORGMODE.plugins["Navigator"].parent(mode="visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('{', Plug('OrgJumpToPreviousVisual', '<Esc>:<C-u>py ORGMODE.plugins["Navigator"].previous(mode="visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding('}', Plug('OrgJumpToNextVisual', '<Esc>:<C-u>py ORGMODE.plugins["Navigator"].next(mode="visual")<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding('g{', Plug('OrgJumpToParentOperator', ':<C-u>py ORGMODE.plugins["Navigator"].parent(mode="operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('{', Plug('OrgJumpToPreviousOperator', ':<C-u>py ORGMODE.plugins["Navigator"].previous(mode="operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding('}', Plug('OrgJumpToNextOperator', ':<C-u>py ORGMODE.plugins["Navigator"].next(mode="operator")<CR>', mode=MODE_OPERATOR)))

		# section wise movement (skip children)
		# normal mode
		self.keybindings.append(Keybinding('[[', Plug('OrgJumpToPreviousSkipChildrenNormal', ':py ORGMODE.plugins["Navigator"].previous(mode="normal", skip_children=True)<CR>')))
		self.menu + ActionEntry('Ne&xt Same Level', self.keybindings[-1])
		self.keybindings.append(Keybinding(']]', Plug('OrgJumpToNextSkipChildrenNormal', ':py ORGMODE.plugins["Navigator"].next(mode="normal", skip_children=True)<CR>')))
		self.menu + ActionEntry('Pre&vious Same Level', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding('[[', Plug('OrgJumpToPreviousSkipChildrenVisual', '<Esc>:<C-u>py ORGMODE.plugins["Navigator"].previous(mode="visual", skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(']]', Plug('OrgJumpToNextSkipChildrenVisual', '<Esc>:<C-u>py ORGMODE.plugins["Navigator"].next(mode="visual", skip_children=True)<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding('[[', Plug('OrgJumpToPreviousSkipChildrenOperator', ':<C-u>py ORGMODE.plugins["Navigator"].previous(mode="operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(']]', Plug('OrgJumpToNextSkipChildrenOperator', ':<C-u>py ORGMODE.plugins["Navigator"].next(mode="operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
