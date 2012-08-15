# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim
from orgmode.liborgmode.checkboxes import Checkbox
from orgmode._vim import ORGMODE

class CheckboxTestCase(unittest.TestCase):

	def setUp(self):
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
		(on, total) = c.all_siblings_status()
		# print "on = %d, total = %d" % (on, total)

	# def test_update_subtask(self):
		# self.set_vim_buffer(buf=self.c2, bufnr=3)
		# h = ORGMODE.get_document(bufnr=3).current_heading()
		# h.init_checkboxes()
		# c = h.current_checkbox(position=3)
		# print c.update_subtask_info()
		
def suite():
	return unittest.TestLoader().loadTestsFromTestCase(
			CheckboxTestCase)

# vim: set noexpandtab:
