# -*- coding: utf-8 -*-

import os
import subprocess

import vim

from orgmode._vim import ORGMODE, echoe, echom
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode import settings


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
	def _get_init_script(cls):
		init_script = settings.get(u'org_export_init_script', u'')
		if init_script:
			init_script = os.path.expandvars(os.path.expanduser(init_script))
			if os.path.exists(init_script):
				return init_script
			else:
				echoe(u'Unable to find init script %s' % init_script)

	@classmethod
	def _export(cls, _format):
		""" Export current file in out format

		:flavor:	pdf or html
		:returns:	return code
		"""
		f = _format if _format == 'pdf' else 'html'
		emacs = os.path.expandvars(os.path.expanduser( \
				settings.get(u'org_export_emacs', u'/usr/bin/emacs')))
		if os.path.exists(emacs):
			cmd = [emacs, u'-nw', u'--batch', u'--visit=%s' \
					% (vim.eval(u'expand("%:p")'), ), \
					u'--funcall=org-export-as-%s' % f]

			# source init script as well
			init_script = cls._get_init_script()
			if init_script:
				cmd.extend(['--script', init_script])
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE, \
					stderr=subprocess.PIPE)
			p.wait()
			if p.returncode != 0 or settings.get(u'org_export_verbose') == 1:
				echom('\n'.join(p.communicate()))

			return p.returncode
		else:
			echoe(u'Unable to find emacs binary %s' % emacs)

	@classmethod
	def topdf(cls):
		u"""
		Export the current buffer as pdf using emacs orgmode.
		"""
		ret = cls._export(u'pdf')
		if ret != 0:
			echoe(u'PDF export failed.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'pdf'))

	@classmethod
	def tohtml(cls):
		u"""
		Export the current buffer as html using emacs orgmode.
		"""
		ret = cls._export(u'html')
		if ret != 0:
			echoe(u'HTML export failed.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'html'))

	def register(self):
		u"""
		Registration and keybindings.
		"""

		# path to emacs executable
		settings.set(u'org_export_emacs', u'/usr/bin/emacs')

		# verbose output for export
		settings.set(u'org_export_verbose', 0)

		# allow the user to define an initialization script
		settings.set(u'org_export_init_script', u'')

		# to PDF
		self.commands.append(Command(u'OrgExportToPDF', \
				u':py ORGMODE.plugins[u"Export"].topdf()<CR>'))
		self.keybindings.append(Keybinding(u'<localleader>ep',
				Plug(u'OrgExportToPDF', self.commands[-1])))
		self.menu + ActionEntry(u'To PDF (via Emacs)', self.keybindings[-1])

		# to HTML
		self.commands.append(Command(u'OrgExportToHTML', \
				u':py ORGMODE.plugins[u"Export"].tohtml()<CR>'))
		self.keybindings.append(Keybinding(u'<localleader>eh',
				Plug(u'OrgExportToHTML', self.commands[-1])))
		self.menu + ActionEntry(u'To HTML (via Emacs)', self.keybindings[-1])

# vim: set noexpandtab:
