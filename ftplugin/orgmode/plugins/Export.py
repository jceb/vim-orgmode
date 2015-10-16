# -*- coding: utf-8 -*-

import os
import subprocess

import vim

from orgmode._vim import ORGMODE, echoe, echom
from orgmode.menu import Submenu, ActionEntry, add_cmd_mapping_menu
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
	def _export(cls, format_):
		"""Export current file to format_.

		:format_:  pdf or html
		:returns:  return code
		"""
		emacsbin = os.path.expandvars(os.path.expanduser(
			settings.get(u'org_export_emacs', u'/usr/bin/emacs')))
		if not os.path.exists(emacsbin):
			echoe(u'Unable to find emacs binary %s' % emacsbin)

		# build the export command
		cmd = [
			emacsbin,
			u'-nw',
			u'--batch',
			u'--visit=%s' % vim.eval(u'expand("%:p")'),
			u'--funcall=%s' % format_
		]
		# source init script as well
		init_script = cls._get_init_script()
		if init_script:
			cmd.extend(['--script', init_script])

		# export
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.wait()

		if p.returncode != 0 or settings.get(u'org_export_verbose') == 1:
			echom('\n'.join(p.communicate()))
		return p.returncode

	@classmethod
	def topdf(cls):
		u"""Export the current buffer as pdf using emacs orgmode."""
		ret = cls._export(u'org-latex-export-to-pdf')
		if ret != 0:
			echoe(u'PDF export failed.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'pdf'))

	@classmethod
	def tohtml(cls):
		u"""Export the current buffer as html using emacs orgmode."""
		ret = cls._export(u'org-html-export-to-html')
		if ret != 0:
			echoe(u'HTML export failed.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'html'))

	@classmethod
	def tolatex(cls):
		u"""Export the current buffer as latex using emacs orgmode."""
		ret = cls._export(u'org-latex-export-to-latex')
		if ret != 0:
			echoe(u'latex export failed.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'tex'))

	@classmethod
	def tomarkdown(cls):
		u"""Export the current buffer as markdown using emacs orgmode."""
		ret = cls._export(u'org-md-export-to-markdown')
		if ret != 0:
			echoe('Markdown export failed. Make sure org-md-export-to-markdown is loaded in emacs, see the manual for details.')
		else:
			echom(u'Export successful: %s.%s' % (vim.eval(u'expand("%:r")'), 'md'))

	def register(self):
		u"""Registration and keybindings."""

		# path to emacs executable
		settings.set(u'org_export_emacs', u'/usr/bin/emacs')
		# verbose output for export
		settings.set(u'org_export_verbose', 0)
		# allow the user to define an initialization script
		settings.set(u'org_export_init_script', u'')

		# to PDF
		add_cmd_mapping_menu(
			self,
			name=u'OrgExportToPDF',
			function=u':py ORGMODE.plugins[u"Export"].topdf()<CR>',
			key_mapping=u'<localleader>ep',
			menu_desrc=u'To PDF (via Emacs)'
		)
		# to latex
		add_cmd_mapping_menu(
			self,
			name=u'OrgExportToLaTeX',
			function=u':py ORGMODE.plugins[u"Export"].tolatex()<CR>',
			key_mapping=u'<localleader>el',
			menu_desrc=u'To LaTeX (via Emacs)'
		)
		# to HTML
		add_cmd_mapping_menu(
			self,
			name=u'OrgExportToHTML',
			function=u':py ORGMODE.plugins[u"Export"].tohtml()<CR>',
			key_mapping=u'<localleader>eh',
			menu_desrc=u'To HTML (via Emacs)'
		)
		# to Markdown
		add_cmd_mapping_menu(
			self,
			name=u'OrgExportToMarkdown',
			function=u':py ORGMODE.plugins[u"Export"].tomarkdown()<CR>',
			key_mapping=u'<localleader>em',
			menu_desrc=u'To Markdown (via Emacs)'
		)

# vim: set noexpandtab:
