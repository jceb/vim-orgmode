# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
sys.path.append(u'../ftplugin')

import unittest
import orgmode.settings
from orgmode.exceptions import PluginError
from orgmode._vim import ORGMODE
from orgmode.keybinding import MODE_ALL, Plug

import vim

from orgmode.py3compat.encode_compatibility import *

ORG_PLUGINS = ['ShowHide', '|', 'Navigator', 'EditStructure', '|', 'Hyperlinks', '|', 'Todo', 'TagsProperties', 'Date', 'Agenda', 'Misc', '|', 'Export']


class MappingTestCase(unittest.TestCase):
	u"""Tests all plugins for overlapping mappings."""
	def test_non_overlapping_plug_mappings(self):
		def find_overlapping_mappings(kb, all_keybindings):
			found_overlapping_mapping = False
			for tkb in all_keybindings:
				if kb.mode == tkb.mode or MODE_ALL in (kb.mode, tkb.mode):
					if isinstance(kb._action, Plug) and isinstance(tkb._action, Plug):
						akb = kb.action
						atkb = tkb.action
						if (akb.startswith(atkb) or atkb.startswith(akb)) and akb != atkb:
							print(u'\nERROR: Found overlapping mapping: %s (%s), %s (%s)' % (kb.key, akb, tkb.key, atkb))
							found_overlapping_mapping = True

			if all_keybindings:
				res = find_overlapping_mappings(all_keybindings[0], all_keybindings[1:])
				if not found_overlapping_mapping:
					return res
			return found_overlapping_mapping

		if self.keybindings:
			self.assertFalse(find_overlapping_mappings(self.keybindings[0], self.keybindings[1:]))

	def setUp(self):
		self.keybindings = []

		vim.EVALRESULTS = {
				u'exists("g:org_debug")': 0,
				u'exists("b:org_debug")': 0,
				u'exists("*repeat#set()")': 0,
				u'b:changedtick': 0,
				u_encode(u'exists("b:org_plugins")'): 0,
				u_encode(u'exists("g:org_plugins")'): 1,
				u_encode(u'g:org_plugins'): ORG_PLUGINS,
				}
		for plugin in filter(lambda p: p != '|', ORG_PLUGINS):
			try:
				ORGMODE.register_plugin(plugin)
			except PluginError:
				pass
			if plugin in ORGMODE._plugins:
				self.keybindings.extend(ORGMODE._plugins[plugin].keybindings)


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(MappingTestCase)

# vi: noexpandtab
