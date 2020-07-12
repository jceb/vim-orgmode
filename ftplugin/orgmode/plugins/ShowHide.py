# -*- coding: utf-8 -*-

import vim

from orgmode.liborgmode.headings import Heading
from orgmode._vim import ORGMODE, apply_count
from orgmode import settings
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, MODE_NORMAL

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.xrange_compatibility import *
from orgmode.py3compat.py_py3_string import *

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
	def _fold_depth(cls, h):
		""" Find the deepest level of open folds

		:h:			Heading
		:returns:	Tuple (int - level of open folds, boolean - found fold) or None if h is not a Heading
		"""
		if not isinstance(h, Heading):
			return

		if int(vim.eval(u_encode(u'foldclosed(%d)' % h.start_vim))) != -1:
			return (h.number_of_parents, True)

		res = [h.number_of_parents + 1]
		found = False
		for c in h.children:
			d, f = cls._fold_depth(c)
			res.append(d)
			found |= f

		return (max(res), found)

	@classmethod
	@apply_count
	def toggle_folding(cls, reverse=False):
		u""" Toggle folding similar to the way orgmode does

		This is just a convenience function, don't hesitate to use the z*
		keybindings vim offers to deal with folding!

		:reverse:	If False open folding by one level otherwise close it by one.
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			vim.eval(u_encode(u'feedkeys("<Tab>", "n")'))
			return

		cursor = vim.current.window.cursor[:]

		if int(vim.eval(u_encode(u'foldclosed(%d)' % heading.start_vim))) != -1:
			if not reverse:
				# open closed fold
				p = heading.number_of_parents
				if not p:
					p = heading.level
				vim.command(u_encode(u'normal! %dzo' % p))
			else:
				# reverse folding opens all folds under the cursor
				vim.command(u_encode(u'%d,%dfoldopen!' % (heading.start_vim, heading.end_of_last_child_vim)))
			vim.current.window.cursor = cursor
			return heading

		def open_fold(h):
			if h.number_of_parents <= open_depth:
				vim.command(u_encode(u'normal! %dgg%dzo' % (h.start_vim, open_depth)))
			for c in h.children:
				open_fold(c)

		def close_fold(h):
			for c in h.children:
				close_fold(c)
			if h.number_of_parents >= open_depth - 1 and \
				int(vim.eval(u_encode(u'foldclosed(%d)' % h.start_vim))) == -1:
				vim.command(u_encode(u'normal! %dggzc' % (h.start_vim, )))

		# find deepest fold
		open_depth, found_fold = cls._fold_depth(heading)

		if not reverse:
			# recursively open folds
			if found_fold:
				for child in heading.children:
					open_fold(child)
			else:
				vim.command(u_encode(u'%d,%dfoldclose!' % (heading.start_vim, heading.end_of_last_child_vim)))

				if heading.number_of_parents:
					# restore cursor position, it might have been changed by open_fold
					vim.current.window.cursor = cursor

					p = heading.number_of_parents
					if not p:
						p = heading.level
					# reopen fold again because the former closing of the fold closed all levels, including parents!
					vim.command(u_encode(u'normal! %dzo' % (p, )))
		else:
			# close the last level of folds
			close_fold(heading)

		# restore cursor position
		vim.current.window.cursor = cursor
		return heading

	@classmethod
	@apply_count
	def global_toggle_folding(cls, reverse=False):
		""" Toggle folding globally

		:reverse:	If False open folding by one level otherwise close it by one.
		"""
		d = ORGMODE.get_document()
		if reverse:
			foldlevel = int(vim.eval(u_encode(u'&foldlevel')))
			if foldlevel == 0:
				# open all folds because the user tries to close folds beyond 0
				vim.eval(u_encode(u'feedkeys("zR", "n")'))
			else:
				# vim can reduce the foldlevel on its own
				vim.eval(u_encode(u'feedkeys("zm", "n")'))
		else:
			found = False
			for h in d.headings:
				res = cls._fold_depth(h)
				if res:
					found = res[1]
				if found:
					break
			if not found:
				# no fold found and the user tries to advance the fold level
				# beyond maximum so close everything
				vim.eval(u_encode(u'feedkeys("zM", "n")'))
			else:
				# fold found, vim can increase the foldlevel on its own
				vim.eval(u_encode(u'feedkeys("zr", "n")'))

		return d

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# register plug

		self.keybindings.append(Keybinding(u'<Tab>',
									 Plug(u'OrgToggleFoldingNormal', u'%s ORGMODE.plugins[u"ShowHide"].toggle_folding()<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'&Cycle Visibility', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Tab>',
									 Plug(u'OrgToggleFoldingReverse', u'%s ORGMODE.plugins[u"ShowHide"].toggle_folding(reverse=True)<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'Cycle Visibility &Reverse', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>.',
									 Plug(u'OrgGlobalToggleFoldingNormal', u'%s ORGMODE.plugins[u"ShowHide"].global_toggle_folding()<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'Cycle Visibility &Globally', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>,',
									 Plug(u'OrgGlobalToggleFoldingReverse',
			   u'%s ORGMODE.plugins[u"ShowHide"].global_toggle_folding(reverse=True)<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'Cycle Visibility Reverse G&lobally', self.keybindings[-1])

		for i in range(0, 10):
			self.keybindings.append(Keybinding(u'<localleader>%d' % (i, ), u'zM:set fdl=%d<CR>' % i, mode=MODE_NORMAL))
