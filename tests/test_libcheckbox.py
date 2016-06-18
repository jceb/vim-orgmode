# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim
from orgmode.liborgmode.checkboxes import Checkbox
from orgmode._vim import ORGMODE

from orgmode.py3compat.encode_compatibility import *

def set_vim_buffer(buf=None, cursor=(2, 0), bufnr=0):
	if buf is None:
		buf = []
	vim.current.buffer[:] = buf
	vim.current.window.cursor = cursor
	vim.current.buffer.number = bufnr


class CheckboxTestCase(unittest.TestCase):

	def setUp(self):
		counter = 0
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONE')],
				u_encode(u'exists("g:org_improve_split_heading")'): u_encode(u'0'),
				u_encode(u'exists("b:org_improve_split_heading")'): u_encode(u'0'),
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("b:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u'&ts'): u_encode(u'8'),
				u_encode(u'exists("g:org_tag_column")'): u_encode(u'0'),
				u_encode(u'exists("b:org_tag_column")'): u_encode(u'0'),
				u_encode(u"v:count"): u_encode(u'0')}

		self.c1 = """
* heading1 [/]
  - [-] checkbox1 [%]
        - [X] checkbox2
        - [ ] checkbox3
  - [X] checkbox4
""".split("\n")

		self.c2 = """
* heading1
  - [ ] checkbox1
  - [ ] checkbox2
        - [ ] checkbox3
              - [ ] checkbox4
                    - [ ] checkbox5
   - [ ] checkbox6
""".split("\n")

	def test_init(self):
		# test initialize Checkbox
		c = Checkbox(level=1, title="checkbox1")
		self.assertEqual(str(c), " - [ ] checkbox1")
		c = Checkbox(level=3, title="checkbox2", status="[X]")
		self.assertEqual(str(c), "   - [X] checkbox2")

	def test_basic(self):
		bufnr = 1
		set_vim_buffer(buf=self.c1, bufnr=bufnr)
		h = ORGMODE.get_document(bufnr=bufnr).current_heading()
		h.init_checkboxes()

		c = h.current_checkbox(position=2)
		self.assertEqual(str(c), self.c1[2])
		self.assertFalse(c.are_children_all(Checkbox.STATUS_ON))
		self.assertTrue(c.is_child_one(Checkbox.STATUS_OFF))
		self.assertFalse(c.are_siblings_all(Checkbox.STATUS_ON))

		for child in c.all_children():
			pass
		for sibling in c.all_siblings():
			pass
		c = h.current_checkbox(position=3)
		new_checkbox = c.copy()
		self.assertEqual(str(c), self.c1[3])
		c.get_parent_list()
		c.get_index_in_parent_list()

	def test_identify(self):
		# test identify_checkbox
		self.assertEqual(Checkbox.identify_checkbox(self.c1[2]), 2)
		self.assertEqual(Checkbox.identify_checkbox(self.c1[3]), 8)
		# check for corner case
		self.assertEqual(Checkbox.identify_checkbox(" - [ ]"), 1)

	def test_toggle(self):
		bufnr = 2
		# test init_checkboxes
		set_vim_buffer(buf=self.c1, bufnr=bufnr)
		h = ORGMODE.get_document(bufnr=bufnr).current_heading()
		h.init_checkboxes()

		# toggle checkbox
		c = h.current_checkbox(position=4)
		c.toggle()
		self.assertEqual(str(c), "        - [X] checkbox3")
		c.toggle()
		self.assertEqual(str(c), "        - [ ] checkbox3")

		(total, on) = c.all_siblings_status()
		self.assertEqual((total, on), (2, 1))

	def test_subtasks(self):
		bufnr = 3
		set_vim_buffer(buf=self.c1, bufnr=bufnr)
		h = ORGMODE.get_document(bufnr=bufnr).current_heading()
		h.init_checkboxes()
		c = h.current_checkbox(position=3)
		c.toggle()
		c = h.current_checkbox(position=2)
		(total, on) = c.all_siblings_status()
		c.update_subtasks(total=total, on=on)
		self.assertEqual(str(c), "  - [-] checkbox1 [50%]")


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(CheckboxTestCase)

# vim: set noexpandtab:
