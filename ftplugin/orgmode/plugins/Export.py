# -*- coding: utf-8 -*-

from orgmode import ORGMODE
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug
from orgmode import settings

import vim


class Export(object):
	u"""
	Export a orgmode file using emacs orgmode.

	This is a *very simple* wrapper of the emacs/orgmode export.  emacs and
	orgmode need to be installed. We simply call emacs with some options to
	export the .org.

	TODO: Offer export options in vim. Don't use the menu.
	TODO: Maybe use a native implementation.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Export')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def topdf(cls):
		u"""
		Export the current buffer as pdf using emacs orgmode.
		"""
		cmd = "!emacs -nw --batch --visit=%:p --funcall=org-export-as-pdf"
		vim.command(cmd)

	@classmethod
	def tohtml(cls):
		u"""
		Export the current buffer as html using emacs orgmode.
		"""
		cmd = "!emacs -nw --batch --visit=%:p --funcall=org-export-as-html"
		vim.command(cmd)

	def register(self):
		u"""
		Registration and keybindings.
		"""

		# to PDF
		self.keybindings.append(Keybinding(u'<localleader>ep',
				Plug(u'OrgExportToPDF',
				u':py ORGMODE.plugins[u"Export"].topdf()<CR>')))
		self.menu + ActionEntry(u'To PDF (via Emacs)', self.keybindings[-1])

		# to HTML
		self.keybindings.append(Keybinding(u'<localleader>eh',
				Plug(u'OrgExportToHTML',
				u':py ORGMODE.plugins[u"Export"].tohtml()<CR>')))
		self.menu + ActionEntry(u'To HTML (via Emacs)', self.keybindings[-1])

# vim: set noexpandtab:
