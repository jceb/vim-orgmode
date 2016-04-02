# -*- coding: utf-8 -*-

import os
import subprocess

import vim

from orgmode._vim import ORGMODE, echoe, echom, get_user_input
from orgmode.menu import Submenu, ActionEntry, add_cmd_mapping_menu
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode import settings


class BabelTangle(object):
	u"""
	Tangle source code blocks using emacs.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Babel')

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
	def _callFunction(cls, function):
		"""Export current file to format_.

		:format_:  elisp function to call
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
			u'--execute=%s' % function
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
	def tangle(cls):
		u"""Tangle all codeblocks of the current buffer"""
		ret = cls._callFunction(u'(funcall \'org-babel-tangle)')
		if ret != 0:
			echoe('Could not tangle file; make sure org-babel-tangle is callable from within emacs.')
		else:
			echom(u'Tangling successful')

	@classmethod
	def tangleFile(cls):
		u"""Tangle all codeblocks of the specified filename"""
		msg = u'Specify filename (relative to current path)'
		filename = get_user_input(msg)
		ret = cls._callFunction(u'(org-babel-tangle-file "'+filename+'")')
		if ret != 0:
			echoe('Could not tangle file; make sure org-babel-tangle-file is callable from within emacs.')
		else:
			echom(u' Successfully tangled file ' + filename + '!')

	def register(self):
		u"""Registration and keybindings."""

		# path to emacs executable
		settings.set(u'org_export_emacs', u'/usr/bin/emacs')
		# verbose output for export
		settings.set(u'org_export_verbose', 0)
		# allow the user to define an initialization script
		settings.set(u'org_export_init_script', u'')

		add_cmd_mapping_menu(
			self,
			name=u'OrgBabelTangle',
			function=u':py ORGMODE.plugins[u"BabelTangle"].tangle()<CR>',
			key_mapping=u'<localleader>cvt',
			menu_desrc=u'Tangle file (via Emacs)'
		)

		add_cmd_mapping_menu(
			self,
			name=u'OrgBabelTangleFile',
			function=u':py ORGMODE.plugins[u"BabelTangle"].tangleFile()<CR>',
			key_mapping=u'<localleader>cvf',
			menu_desrc=u'Tangle file (via Emacs)'
		)

# vim: set noexpandtab:
