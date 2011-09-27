# -*- coding: utf-8 -*-

from orgmode import echo, ORGMODE, apply_count
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, MODE_VISUAL, MODE_OPERATOR, Plug
from orgmode.liborgmode.documents import Direction

import vim

class Navigator(object):
	u""" Implement navigation in org-mode documents """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + Submenu(u'&Navigate Headings')
		self.keybindings = []

	@classmethod
	@apply_count
	def parent(cls, mode):
		u"""
		Focus parent heading

		:returns: parent heading or None
		"""
		heading = ORGMODE.get_document().current_heading()
		if not heading:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No heading found')
			return

		if not heading.parent:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No parent heading found')
			return

		p = heading.parent

		if mode == u'visual':
			cls._change_visual_selection(heading, p, direction=Direction.BACKWARD, parent=True)
		else:
			vim.current.window.cursor = (p.start_vim, p.level + 1)
		return p

	@classmethod
	@apply_count
	def parent_next_sibling(cls, mode):
		u"""
		Focus the parent's next sibling

		:returns: parent's next sibling heading or None
		"""
		heading = ORGMODE.get_document().current_heading()
		if not heading:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No heading found')
			return

		if not heading.parent or not heading.parent.next_sibling:
			if mode == u'visual':
				vim.command(u'normal! gv'.encode(u'utf-8'))
			else:
				echo(u'No parent heading found')
			return

		ns = heading.parent.next_sibling

		if mode == u'visual':
			cls._change_visual_selection(heading, ns, direction=Direction.FORWARD, parent=False)
		elif mode == u'operator':
			vim.current.window.cursor = (ns.start_vim, 0)
		else:
			vim.current.window.cursor = (ns.start_vim, ns.level + 1)
		return ns

	@classmethod
	def _change_visual_selection(cls, current_heading, heading, direction=Direction.FORWARD, noheadingfound=False, parent=False):
		current = vim.current.window.cursor[0]
		line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
		line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]

		f_start = heading.start_vim
		f_end = heading.end_vim
		swap_cursor = True

		# << |visual start
		# selection end >>
		if current == line_start:
			if (direction == Direction.FORWARD and line_end < f_start) or noheadingfound and not direction == Direction.BACKWARD:
				swap_cursor = False

			# focus heading HERE
			# << |visual start
			# selection end >>

			# << |visual start
			# focus heading HERE
			# selection end >>
			if f_start < line_start and direction == Direction.BACKWARD:
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
				if direction == Direction.FORWARD:
					if line_end < f_start and not line_start == f_start - 1 and current_heading:
						# focus end of previous heading instead of beginning of next heading
						line_start = line_end
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_start = line_end
						line_end = f_end
				elif direction == Direction.BACKWARD:
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

			elif (line_start > f_start or \
					line_start == f_start) and line_end <= f_end and direction == Direction.BACKWARD:
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
				if direction == Direction.FORWARD:
					if line_end < f_start - 1:
						# focus end of previous heading instead of beginning of next heading
						line_end = f_start - 1
					else:
						# focus end of next heading
						line_end = f_end
				else:
					line_end = f_end
				swap_cursor = False

		move_col_start = u'%dl' % (col_start - 1) if (col_start - 1) > 0 and (col_start - 1) < 2000000000 else u''
		move_col_end = u'%dl' % (col_end - 1) if (col_end - 1) > 0 and (col_end - 1) < 2000000000 else u''
		swap = u'o' if swap_cursor else u''

		vim.command((u'normal! %dgg%s%s%dgg%s%s' % \
				(line_start, move_col_start, vim.eval(u'visualmode()'.encode(u'utf-8')), line_end, move_col_end, swap)).encode(u'utf-8'))

	@classmethod
	def _focus_heading(cls, mode, direction=Direction.FORWARD, skip_children=False):
		u"""
		Focus next or previous heading in the given direction

		:direction: True for next heading, False for previous heading
		:returns: next heading or None
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		heading = current_heading
		focus_heading = None
		# FIXME this is just a piece of really ugly and unmaintainable code. It
		# should be rewritten
		if not heading:
			if direction == Direction.FORWARD and d.headings \
					and vim.current.window.cursor[0] < d.headings[0].start_vim:
				# the cursor is in the meta information are, therefore focus
				# first heading
				focus_heading = d.headings[0]
			if not (heading or focus_heading):
				if mode == u'visual':
					# restore visual selection when no heading was found
					vim.command(u'normal! gv'.encode(u'utf-8'))
				else:
					echo(u'No heading found')
				return
		elif direction == Direction.BACKWARD:
			if vim.current.window.cursor[0] != heading.start_vim:
				# the cursor is in the body of the current heading, therefore
				# the current heading will be focused
				if mode == u'visual':
					line_start, col_start = [ int(i) for i in vim.eval(u'getpos("\'<")'.encode(u'utf-8'))[1:3] ]
					line_end, col_end = [ int(i) for i in vim.eval(u'getpos("\'>")'.encode(u'utf-8'))[1:3] ]
					if line_start >= heading.start_vim and line_end > heading.start_vim:
						focus_heading = heading
				else:
					focus_heading = heading

		# so far no heading has been found that the next focus should be on
		if not focus_heading:
			if not skip_children and direction == Direction.FORWARD and heading.children:
				focus_heading = heading.children[0]
			elif direction == Direction.FORWARD and heading.next_sibling:
				focus_heading = heading.next_sibling
			elif direction == Direction.BACKWARD and heading.previous_sibling:
				focus_heading = heading.previous_sibling
				if not skip_children:
					while focus_heading.children:
						focus_heading = focus_heading.children[-1]
			else:
				if direction == Direction.FORWARD:
					focus_heading = current_heading.next_heading
				else:
					focus_heading = current_heading.previous_heading

		noheadingfound = False
		if not focus_heading:
			if mode in (u'visual', u'operator'):
				# the cursor seems to be on the last or first heading of this
				# document and performes another next/previous operation
				focus_heading = heading
				noheadingfound = True
			else:
				if direction == Direction.FORWARD:
					echo(u'Already focussing last heading')
				else:
					echo(u'Already focussing first heading')
				return

		if mode == u'visual':
			cls._change_visual_selection(current_heading, focus_heading, direction=direction, noheadingfound=noheadingfound)
		elif mode == u'operator':
			if direction == Direction.FORWARD and vim.current.window.cursor[0] >= focus_heading.start_vim:
				vim.current.window.cursor = (focus_heading.end_vim, len(vim.current.buffer[focus_heading.end].decode(u'utf-8')))
			else:
				vim.current.window.cursor = (focus_heading.start_vim, 0)
		else:
			vim.current.window.cursor = (focus_heading.start_vim, focus_heading.level + 1)
		if noheadingfound:
			return
		return focus_heading

	@classmethod
	@apply_count
	def previous(cls, mode, skip_children=False):
		u"""
		Focus previous heading
		"""
		return cls._focus_heading(mode, direction=Direction.BACKWARD, skip_children=skip_children)

	@classmethod
	@apply_count
	def next(cls, mode, skip_children=False):
		u"""
		Focus next heading
		"""
		return cls._focus_heading(mode, direction=Direction.FORWARD, skip_children=skip_children)

	def register(self):
		# normal mode
		self.keybindings.append(Keybinding(u'g{', Plug('OrgJumpToParentNormal', u':py ORGMODE.plugins[u"Navigator"].parent(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Up', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingNormal', u':py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Down', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousNormal', u':py ORGMODE.plugins[u"Navigator"].previous(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Previous', self.keybindings[-1])
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextNormal', u':py ORGMODE.plugins[u"Navigator"].next(mode=u"normal")<CR>')))
		self.menu + ActionEntry(u'&Next', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding(u'g{', Plug(u'OrgJumpToParentVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].parent(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"visual")<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"visual")<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding(u'g{', Plug(u'OrgJumpToParentOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].parent(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'g}', Plug('OrgJumpToParentsSiblingOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].parent_next_sibling(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'{', Plug(u'OrgJumpToPreviousOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"operator")<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u'}', Plug(u'OrgJumpToNextOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"operator")<CR>', mode=MODE_OPERATOR)))

		# section wise movement (skip children)
		# normal mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenNormal', u':py ORGMODE.plugins[u"Navigator"].previous(mode=u"normal", skip_children=True)<CR>')))
		self.menu + ActionEntry(u'Ne&xt Same Level', self.keybindings[-1])
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenNormal', u':py ORGMODE.plugins[u"Navigator"].next(mode=u"normal", skip_children=True)<CR>')))
		self.menu + ActionEntry(u'Pre&vious Same Level', self.keybindings[-1])

		# visual mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"visual", skip_children=True)<CR>', mode=MODE_VISUAL)))
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenVisual', u'<Esc>:<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"visual", skip_children=True)<CR>', mode=MODE_VISUAL)))

		# operator-pending mode
		self.keybindings.append(Keybinding(u'[[', Plug(u'OrgJumpToPreviousSkipChildrenOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].previous(mode=u"operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
		self.keybindings.append(Keybinding(u']]', Plug(u'OrgJumpToNextSkipChildrenOperator', u':<C-u>py ORGMODE.plugins[u"Navigator"].next(mode=u"operator", skip_children=True)<CR>', mode=MODE_OPERATOR)))
