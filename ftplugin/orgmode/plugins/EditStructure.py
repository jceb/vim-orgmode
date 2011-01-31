# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_INSERT, MODE_NORMAL
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

	def new_heading(self, below=None, insert_mode=False, end_of_last_child=False):
		h = Heading.current_heading()
		cursor = vim.current.window.cursor[:]
		if not h:
			pos = cursor[0] - 1
			tmp = vim.current.buffer[pos]
			del vim.current.buffer[pos]
			vim.current.buffer[pos:pos] = ['%s %s' % ('*', tmp.lstrip())]
			vim.current.window.cursor = (pos + 1, cursor[1] + 1 + 1)
			return

		# it's weird but this is the behavior of original orgmode
		if below == None:
			below = cursor[1] != 0 or end_of_last_child

		if below:
			if end_of_last_child:
				pos = h.end_of_last_child_vim
			else:
				pos = h.end_vim
			level = h.level
		else:
			pos = h.start_vim - 1
			level = h.level

		# if cursor is currently on a heading, insert parts of it into the
		# newly created heading
		if  insert_mode and not end_of_last_child and cursor[0] == h.start_vim:
			if cursor[1] > h.level:
				tmp1 = vim.current.buffer[cursor[0] - 1][:cursor[1]]
				tmp2 = vim.current.buffer[cursor[0] - 1][cursor[1]:]
				vim.current.buffer[cursor[0] - 1] = tmp1
			else:
				tmp2 = ''
			if below:
				vim.current.buffer[cursor[0]:cursor[0]] = ['%s %s' % ('*' * level, tmp2.lstrip())]
				vim.current.window.cursor = (cursor[0] + 1, level + 1)
			else:
				# this can only happen at column 0
				vim.current.buffer[cursor[0] - 1:cursor[0] - 1] = ['%s ' % ('*' * level, )]
				vim.current.window.cursor = (cursor[0], level + 1)
		elif insert_mode and not below and not end_of_last_child:
			vim.current.buffer[cursor[0] - 1] = '%s %s' % ('*' * level, vim.current.buffer[cursor[0] - 1].lstrip())
			vim.current.window.cursor = (cursor[0], cursor[1] + level + 1)
		else:
			vim.current.buffer[pos:pos] = vim.current.buffer[pos:pos] + ['%s ' % ('*' * level, )]
			vim.command('exe "normal %dgg"|startinsert!' % (pos + 1, ))

		# not sure what to return here .. line number of new heading or old heading object?
		return h

	def _change_heading_level(self, level, including_children=True, on_heading=False):
		"""
		Change level of heading realtively with or without including children.
		"""
		h = Heading.current_heading()
		if not h or on_heading and h.start_vim != vim.current.window.cursor[0]:
			# TODO figure out the actually pressed keybinding and feed these
			# keys instead of making keys up like this
			if level > 0:
				if including_children:
					vim.eval('feedkeys(">]]", "n")')
				elif on_heading:
					vim.eval('feedkeys(">>", "n")')
				else:
					vim.eval('feedkeys(">}", "n")')
			else:
				if including_children:
					vim.eval('feedkeys("<]]", "n")')
				elif on_heading:
					vim.eval('feedkeys("<<", "n")')
				else:
					vim.eval('feedkeys("<}", "n")')
			# return True because otherwise apply_count will not work
			return True

		# don't allow demotion below level 1
		if h.level == 1 and level < 1:
			return False

		# reduce level of demotion to a minimum heading level of 1
		if (h.level + level) < 1:
			level = 1

		def indent(heading, ic):
			if not heading:
				return
			end_vim = heading.end_vim
			# strip level and add new level
			vim.current.buffer[heading.start] = '%s%s' % ('*' * (heading.level + level), \
					vim.current.buffer[heading.start][heading.level:])

			if ic:
				for child in heading.children:
					res = indent(child, ic)
					if res > end_vim:
						end_vim = res
			return end_vim

		# save cursor position
		c = vim.current.window.cursor[:]
		# figure out the end of the last child before changing anything within the vim buffer
		h.end_of_last_child
		# indent the promoted/demoted heading
		vim.command('normal %dggV%dgg=' % (h.start_vim, indent(h, including_children)))
		# restore cursor position
		vim.current.window.cursor = (c[0], c[1] + level)

		return True

	@repeat
	@apply_count
	def demote_heading(self, including_children=True, on_heading=False):
		if self._change_heading_level(-1, including_children=including_children, on_heading=on_heading):
			if including_children:
				return 'OrgDemoteSubtree'
			return 'OrgDemoteHeading'

	@repeat
	@apply_count
	def promote_heading(self, including_children=True, on_heading=False):
		if self._change_heading_level(1, including_children=including_children, on_heading=on_heading):
			if including_children:
				return 'OrgPromoteSubtreeNormal'
			return 'OrgPromoteHeadingNormal'

	def _move_heading(self, direction=DIRECTION_FORWARD):
		""" Move heading up or down

		:returns: heading or None
		"""
		heading = Heading.current_heading()
		if not heading or \
				direction == DIRECTION_FORWARD and not heading.next_sibling or \
				direction == DIRECTION_BACKWARD and not heading.previous_sibling:
			return None

		replaced_heading = None
		if direction == DIRECTION_FORWARD:
			replaced_heading = heading.next_sibling
		else:
			replaced_heading = heading.previous_sibling

		# move heading including all sub heading upwards
		save_next_previous_sibling = vim.current.buffer[replaced_heading.start:replaced_heading.end_of_last_child + 1]
		save_current_heading = vim.current.buffer[heading.start:heading.end_of_last_child + 1]

		new_end_of_last_child = None
		new_start = None
		new_cursor_position = None
		old_start = None
		old_end_of_last_child = None

		if direction == DIRECTION_FORWARD:
			new_start = replaced_heading.end_of_last_child - (heading.end_of_last_child - heading.start)
			new_end_of_last_child = replaced_heading.end_of_last_child
			new_cursor_position = vim.current.window.cursor[0] + (new_start - heading.start)
			old_start = heading.start
			old_end_of_last_child = new_start
		else:
			new_start = replaced_heading.start
			new_end_of_last_child = replaced_heading.start + heading.end_of_last_child - heading.start
			new_cursor_position = vim.current.window.cursor[0] - (heading.start - new_start)
			old_start = new_end_of_last_child + 1
			old_end_of_last_child = heading.end_of_last_child + 1

		vim.current.buffer[new_start:new_end_of_last_child + 1] = save_current_heading
		vim.current.buffer[old_start:old_end_of_last_child] = save_next_previous_sibling

		vim.current.window.cursor = (new_cursor_position, vim.current.window.cursor[1])

		return True

	@repeat
	@apply_count
	def move_heading_upward(self):
		if self._move_heading(direction=DIRECTION_BACKWARD):
			return 'OrgMoveHeadingUpward'

	@repeat
	@apply_count
	def move_heading_downward(self):
		if self._move_heading(direction=DIRECTION_FORWARD):
			return 'OrgMoveHeadingDownward'

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding('<C-S-CR>', Plug('OrgNewHeadingAboveNormal', ':silent! py ORGMODE.plugins["EditStructure"].new_heading(below=False)<CR>')))
		self.menu + ActionEntry('New Heading &above', self.keybindings[-1])
		self.keybindings.append(Keybinding('<S-CR>', Plug('OrgNewHeadingBelowNormal', ':silent! py ORGMODE.plugins["EditStructure"].new_heading(below=True)<CR>')))
		self.menu + ActionEntry('New Heading &below', self.keybindings[-1])
		self.keybindings.append(Keybinding('<C-CR>', Plug('OrgNewHeadingBelowAfterChildrenNormal', ':silent! py ORGMODE.plugins["EditStructure"].new_heading(below=True, end_of_last_child=True)<CR>')))
		self.menu + ActionEntry('New Heading below, after &children', self.keybindings[-1])

		self.keybindings.append(Keybinding('<C-S-CR>', Plug('OrgNewHeadingAboveInsert', '<C-o>:<C-u>silent! py ORGMODE.plugins["EditStructure"].new_heading(below=False, insert_mode=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding('<S-CR>', Plug('OrgNewHeadingBelowInsert', '<C-o>:<C-u>silent! py ORGMODE.plugins["EditStructure"].new_heading(insert_mode=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding('<C-CR>', Plug('OrgNewHeadingBelowAfterChildrenInsert', '<C-o>:<C-u>silent! py ORGMODE.plugins["EditStructure"].new_heading(insert_mode=True, end_of_last_child=True)<CR>', mode=MODE_INSERT)))

		self.menu + Separator()

		self.keybindings.append(Keybinding('m[[', Plug('OrgMoveHeadingUpward', ':silent! py ORGMODE.plugins["EditStructure"].move_heading_upward()<CR>')))
		self.menu + ActionEntry('Move Subtree &Up', self.keybindings[-1])
		self.keybindings.append(Keybinding('m]]', Plug('OrgMoveHeadingDownward', ':silent! py ORGMODE.plugins["EditStructure"].move_heading_downward()<CR>')))
		self.menu + ActionEntry('Move Subtree &Down', self.keybindings[-1])

		self.menu + Separator()

		self.menu + ActionEntry('&Copy Heading', 'yah', 'yah')
		self.menu + ActionEntry('C&ut Heading', 'dah', 'dah')

		self.menu + Separator()

		self.menu + ActionEntry('&Copy Subtree', 'yat', 'yat')
		self.menu + ActionEntry('C&ut Subtree', 'dat', 'dat')
		self.menu + ActionEntry('&Paste Subtree', 'p', 'p')

		self.menu + Separator()

		self.keybindings.append(Keybinding('>ah', Plug('OrgPromoteHeadingNormal', ':silent! py ORGMODE.plugins["EditStructure"].promote_heading(including_children=False)<CR>')))
		self.menu + ActionEntry('&Promote Heading', self.keybindings[-1])
		self.keybindings.append(Keybinding('>>', Plug('OrgPromoteOnHeadingNormal', ':silent! py ORGMODE.plugins["EditStructure"].promote_heading(including_children=False, on_heading=True)<CR>')))
		self.keybindings.append(Keybinding('>}', '<Plug>OrgPromoteHeadingNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding('>ih', '<Plug>OrgPromoteHeadingNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding('>at', Plug('OrgPromoteSubtreeNormal', ':silent! py ORGMODE.plugins["EditStructure"].promote_heading()<CR>')))
		self.menu + ActionEntry('&Promote Subtree', self.keybindings[-1])
		self.keybindings.append(Keybinding('>]]', '<Plug>OrgPromoteSubtreeNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding('>it', '<Plug>OrgPromoteSubtreeNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding('<ah', Plug('OrgDemoteHeadingNormal', ':silent! py ORGMODE.plugins["EditStructure"].demote_heading(including_children=False)<CR>')))
		self.menu + ActionEntry('&Demote Heading', self.keybindings[-1])
		self.keybindings.append(Keybinding('<<', Plug('OrgDemoteOnHeadingNormal', ':silent! py ORGMODE.plugins["EditStructure"].demote_heading(including_children=False, on_heading=True)<CR>')))
		self.keybindings.append(Keybinding('<{', '<Plug>OrgDemoteHeadingNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding('<ih', '<Plug>OrgDemoteHeadingNormal', mode=MODE_NORMAL))

		self.keybindings.append(Keybinding('<at', Plug('OrgDemoteSubtreeNormal', ':silent! py ORGMODE.plugins["EditStructure"].demote_heading()<CR>')))
		self.menu + ActionEntry('&Demote Subtree', self.keybindings[-1])
		self.keybindings.append(Keybinding('<[[', '<Plug>OrgDemoteSubtreeNormal', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding('<it', '<Plug>OrgDemoteSubtreeNormal', mode=MODE_NORMAL))

		# other keybindings
		self.keybindings.append(Keybinding('<C-t>', Plug('OrgPromoteOnHeadingInsert', '<C-o>:silent! py ORGMODE.plugins["EditStructure"].promote_heading(including_children=False, on_heading=True)<CR>', mode=MODE_INSERT)))
		self.keybindings.append(Keybinding('<C-d>', Plug('OrgDemoteOnHeadingInsert', '<C-o>:silent! py ORGMODE.plugins["EditStructure"].demote_heading(including_children=False, on_heading=True)<CR>', mode=MODE_INSERT)))
