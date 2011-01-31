# -*- coding: utf-8 -*-

from orgmode import settings
from orgmode import echo, echom, echoe, ORGMODE, apply_count
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_NORMAL
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class ShowHide(object):
	""" Example plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('&Show Hide')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []
	
	@apply_count
	def toggle_folding(self):
		""" Toggle folding similar to the way orgmode does

		This is just a convenience function, don't hesitate to use the z*
		keybindings vim offers to deal with folding!
		"""
		heading = Heading.current_heading()
		if not heading:
			vim.eval('feedkeys("<Tab>", "n")')
			return

		cursor = vim.current.window.cursor[:]

		if int(vim.eval('foldclosed(%d)' % heading.start_vim)) != -1:
			# open closed fold
			vim.command('normal %dzo' % heading.number_of_parents)
			vim.current.window.cursor = cursor
			return heading

		found_fold = False
		open_depth = 0

		def fold_depth(h):
			if int(vim.eval('foldclosed(%d)' % h.start_vim)) != -1:
				return (h.number_of_parents, True)
			else:
				res = [h.number_of_parents + 1]
				found = False

				for c in h.children:
					d, f = fold_depth(c)
					res.append(d)
					found |= f

				return (max(res), found)

		def open_fold(h):
			if h.number_of_parents <= open_depth:
				vim.command('normal %dgg%dzo' % (h.start_vim, open_depth))
			if h.children:
				for c in h.children:
					open_fold(c)

		# find deepest fold
		open_depth, found_fold = fold_depth(heading)
		open_depth = open_depth

		# recursively open folds
		for child in heading.children:
			# find deepest fold
			if found_fold:
				open_fold(child)

		if not found_fold:
			vim.command('%d,%dfoldclose!' % (heading.start_vim, heading.end_of_last_child_vim))

			if heading.number_of_parents:
				# restore cursor position, it might have been changed by open_fold
				vim.current.window.cursor = cursor

				# reopen fold again beacause the former closing of the fold closed all levels, including parents!
				vim.command('normal %dzo' % (heading.number_of_parents, ))

		# restore cursor position
		vim.current.window.cursor = cursor
		return heading

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# register plug
		
		self.keybindings.append(Keybinding('<Tab>', Plug('OrgToggleFolding', ':silent! py ORGMODE.plugins["ShowHide"].toggle_folding()<CR>')))
		self.menu + ActionEntry('&Cycle Visibility', self.keybindings[-1])

		settings.set('org_leader', ',')
		leader = settings.get('org_leader', ',')

		self.keybindings.append(Keybinding('%s,' % (leader, ), ':exe ":set fdl=". (&fdl - 1)<CR>', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding('%s.' % (leader, ), ':exe ":set fdl=". (&fdl + 1)<CR>', mode=MODE_NORMAL))
		for i in xrange(0, 10):
			self.keybindings.append(Keybinding('%s%d' % (leader, i), 'zM:set fdl=%d<CR>' % i, mode=MODE_NORMAL))
