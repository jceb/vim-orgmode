# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim
from orgmode.liborgmode.checkboxes import Checkbox
from orgmode._vim import ORGMODE

class CheckboxTestCase(unittest.TestCase):

	def setUp(self):
		counter = 0
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u'exists("b:org_todo_keywords")'.encode(u'utf-8'): '0'.encode(u'utf-8'),
				# global values for org_todo_keywords
				u'exists("g:org_todo_keywords")'.encode(u'utf-8'): '1'.encode(u'utf-8'),
				u'g:org_todo_keywords'.encode(u'utf-8'): [u'TODO'.encode(u'utf-8'), u'DONE'.encode(u'utf-8'), u'|'.encode(u'utf-8')],
				u'exists("g:org_improve_split_heading")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_improve_split_heading")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("g:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("*repeat#set()")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'b:changedtick'.encode(u'utf-8'): (u'%d' % counter).encode(u'utf-8'),
				u'&ts'.encode(u'utf-8'): u'8'.encode(u'utf-8'),
				u'exists("g:org_tag_column")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_tag_column")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u"v:count".encode(u'utf-8'): u'0'.encode(u'utf-8')}
		self.c1 = """
* heading1
 - [ ] checkbox1
  - [ ] checkbox2
 - [X] checkbox3
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

	
	def set_vim_buffer(self, buf=[], cursor=(2, 0), bufnr=0):
		vim.current.buffer[:] = buf
		vim.current.window.cursor = cursor 
		vim.current.buffer.number = bufnr

	def test_init(self):
		# test initialize Checkbox
		c = Checkbox(level=1, title="checkbox1")
		self.assertEqual(str(c), " - [ ] checkbox1")
		c = Checkbox(level=3, title="checkbox2", status="[X]")
		self.assertEqual(str(c)," " * 3 + "- [X] checkbox2")
	
	def test_identify(self):
		# test identify_checkbox
		self.assertEqual(Checkbox.identify_checkbox(self.c1[2]), 1)
		self.assertEqual(Checkbox.identify_checkbox(self.c1[3]), 2)
		# check for corner case
		self.assertEqual(Checkbox.identify_checkbox(" - [ ]"), 1)

	def test_toggle(self):
		# test init_checkboxes 
		self.set_vim_buffer(buf=self.c1, bufnr=1)
		h = ORGMODE.get_document(bufnr=1).current_heading()
		h.init_checkboxes()
		# list all checkboxes
		top_level_checkboxes = [" - [ ] checkbox1",
								" - [X] checkbox3"]
		i = 0
		for c in h.all_toplevel_checkboxes():
			# self.assertEqual(str(c), top_level_checkboxes[i])
			# print c
			i += 1

		# toggle checkbox
		c = h.current_checkbox(position=4)
		c.toggle()
		self.assertEqual(str(c), " - [ ] checkbox3")
		c.toggle()
		self.assertEqual(str(c), " - [X] checkbox3")

		# test init_checkboxes 
		self.set_vim_buffer(buf=self.c2, bufnr=2)
		h = ORGMODE.get_document(bufnr=2).current_heading()
		h.init_checkboxes()
		c = h.current_checkbox(position=2)

		# print c
		(total, on) = c.all_siblings_status()
		# print "on = %d, total = %d" % (on, total)
		self.assertEqual((total, on), (2, 0))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(
			CheckboxTestCase)

# vim: set noexpandtab:
