# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

PLUGIN_NAME = u'EditCheckbox'

bufnr = 10

def set_vim_buffer(buf=None, cursor=(2, 0), bufnr=0):
	if buf is None:
		buf = []
	vim.current.buffer[:] = buf
	vim.current.window.cursor = cursor
	vim.current.buffer.number = bufnr


class EditCheckboxTestCase(unittest.TestCase):
	def setUp(self):
		if PLUGIN_NAME not in ORGMODE.plugins:
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
              - [ ] checkbox7
              - [ ] checkbox8
""".split(u'\n')

		self.c2 = u"""
* a checkbox list [%]
  - checkbox [0%]
        - [ ] test1
        - [ ] test2
        - [ ] test3
""".split(u'\n')

		self.c3 = u"""
* heading
  1. [ ] another main task [%]
         - [ ] sub task 1
         - [ ] sub task 2
  2. [ ] another main task
""".split(u'\n')

	def test_toggle(self):
		global bufnr
		bufnr += 1
		# test on self.c1
		set_vim_buffer(buf=self.c1, cursor=(6, 0), bufnr=bufnr)
		# update_checkboxes_status
		self.editcheckbox.update_checkboxes_status()
		self.assertEqual(vim.current.buffer[1], "* heading1 [0%]")
		# toggle
		self.editcheckbox.toggle()
		self.assertEqual(vim.current.buffer[5], "              - [X] checkbox4")

		bufnr += 1
		set_vim_buffer(buf=self.c1, cursor=(9, 0), bufnr=bufnr)
		# toggle and check checkbox status
		self.editcheckbox.toggle()
		self.assertEqual(vim.current.buffer[8], "              - [X] checkbox7")
		self.assertEqual(vim.current.buffer[7], "        - [-] checkbox6")
		self.assertEqual(vim.current.buffer[6], "  - [-] checkbox5")

		# new_checkbox
		vim.current.window.cursor = (10, 0)
		self.editcheckbox.new_checkbox(below=True)
		self.assertEqual(vim.current.buffer[10], '              - [ ] ')
		self.editcheckbox.update_checkboxes_status()

	def test_no_status_checkbox(self):
		global bufnr
		bufnr += 1
		# test on self.c2
		set_vim_buffer(buf=self.c2, bufnr=bufnr)
		self.assertEqual(vim.current.buffer[2], "  - checkbox [0%]")
		# toggle
		vim.current.window.cursor = (4, 0)
		self.editcheckbox.toggle()
		self.assertEqual(vim.current.buffer[3], "        - [X] test1")

		# self.editcheckbox.update_checkboxes_status()
		# see if the no status checkbox update its status
		self.assertEqual(vim.current.buffer[2], "  - checkbox [33%]")

	def test_number_list(self):
		global bufnr
		bufnr += 1
		set_vim_buffer(buf=self.c3, bufnr=bufnr)
		vim.current.window.cursor = (6, 0)
		self.editcheckbox.toggle()
		self.assertEqual(vim.current.buffer[5], "  2. [X] another main task")


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(EditCheckboxTestCase)

# vim: set noexpandtab:
