# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

PLUGIN_NAME = u'EditCheckbox'

class EditCheckboxTestCase(unittest.TestCase):
	def setUp(self):
		if not PLUGIN_NAME in ORGMODE.plugins:
			ORGMODE.register_plugin(PLUGIN_NAME)
		self.editcheckbox = ORGMODE.plugins[PLUGIN_NAME]
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* heading1
 - [ ] checkbox1
  - [ ] checkbox2
  - [ ] checkbox3
    - [ ] checkbox4
 - [ ] checkbox5
  - [ ] checkbox6
""".split(u'\n')]

	def test_toggle(self):
		vim.current.window.cursor = (6, 0)
		self.editcheckbox.toggle()
		# print "\n".join(vim.current.buffer)

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(EditCheckboxTestCase)
