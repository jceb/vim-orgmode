# -*- coding: utf-8 -*-

from orgmode import settings
from orgmode import ORGMODE, apply_count
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_NORMAL

import vim

class ShowHide(object):
	u""" Show Hide plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&Show Hide')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	@apply_count
	def toggle_folding(cls):
		u""" Toggle folding similar to the way orgmode does

		This is just a convenience function, don't hesitate to use the z*
		keybindings vim offers to deal with folding!
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			vim.eval(u'feedkeys("<Tab>", "n")'.encode(u'utf-8'))
			return

		cursor = vim.current.window.cursor[:]

		if int(vim.eval((u'foldclosed(%d)' % heading.start_vim).encode(u'utf-8'))) != -1:
			# open closed fold
			p = heading.number_of_parents
			if not p:
				p = heading.level
			vim.command((u'normal %dzo' % p).encode(u'utf-8'))
			vim.current.window.cursor = cursor
			return heading

		found_fold = False
		open_depth = 0

		def fold_depth(h):
			if int(vim.eval((u'foldclosed(%d)' % h.start_vim).encode(u'utf-8'))) != -1:
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
				vim.command((u'normal %dgg%dzo' % (h.start_vim, open_depth)).encode(u'utf-8'))
			if h.children:
				for c in h.children:
					open_fold(c)

		# find deepest fold
		open_depth, found_fold = fold_depth(heading)

		# recursively open folds
		for child in heading.children:
			# find deepest fold
			if found_fold:
				open_fold(child)

		if not found_fold:
			vim.command((u'%d,%dfoldclose!' % (heading.start_vim, heading.end_of_last_child_vim)).encode(u'utf-8'))

			if heading.number_of_parents:
				# restore cursor position, it might have been changed by open_fold
				vim.current.window.cursor = cursor

				p = heading.number_of_parents
				if not p:
					p = heading.level
				# reopen fold again beacause the former closing of the fold closed all levels, including parents!
				vim.command((u'normal %dzo' % (p, )).encode(u'utf-8'))

		# restore cursor position
		vim.current.window.cursor = cursor
		return heading

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# register plug

		self.keybindings.append(Keybinding(u'<Tab>', Plug(u'OrgToggleFolding', u':py ORGMODE.plugins[u"ShowHide"].toggle_folding()<CR>')))
		self.menu + ActionEntry(u'&Cycle Visibility', self.keybindings[-1])

		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%s,' % (leader, ), u':exe ":set fdl=". (&fdl - 1)<CR>', mode=MODE_NORMAL))
		self.keybindings.append(Keybinding(u'%s.' % (leader, ), u':exe ":set fdl=". (&fdl + 1)<CR>', mode=MODE_NORMAL))
		for i in xrange(0, 10):
			self.keybindings.append(Keybinding(u'%s%d' % (leader, i), u'zM:set fdl=%d<CR>' % i, mode=MODE_NORMAL))
