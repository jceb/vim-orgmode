# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

PLUGIN_NAME = u'EditCheckbox'

def set_vim_buffer(buf=[], cursor=(2, 0), bufnr=0):
	vim.current.buffer[:] = buf
	vim.current.window.cursor = cursor 
	vim.current.buffer.number = bufnr

class EditCheckboxTestCase(unittest.TestCase):
	def setUp(self):
		if not PLUGIN_NAME in ORGMODE.plugins:
			ORGMODE.register_plugin(PLUGIN_NAME)
		self.editcheckbox = ORGMODE.plugins[PLUGIN_NAME]
		self.c1 = u"""
* heading1 [%]
 - [ ] checkbox1 [/]
  - [ ] checkbox2
  - [ ] checkbox3
    - [ ] checkbox4
 - [ ] checkbox5
  - [ ] checkbox6
""".split(u'\n')

	def test_toggle(self):
		set_vim_buffer(self.c1, cursor=(6, 0))
		# update_checkboxes_status
		self.editcheckbox.update_checkboxes_status()
		self.assertEqual(vim.current.buffer[1], "* heading1 [0%]")
		# toggle
		self.editcheckbox.toggle()
		self.assertEqual(vim.current.buffer[5],"    - [X] checkbox4")
		vim.current.window.cursor = (7, 0)
		# new_checkbox
		self.editcheckbox.new_checkbox(below=True)
		self.assertEqual(vim.current.buffer[8], ' - [ ] ')

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(EditCheckboxTestCase)
