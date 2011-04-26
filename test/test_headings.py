# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode.liborgmode import Document

class HeadingTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0}
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')

	def test_no_heading(self):
		# test no heading
		vim.current.window.cursor = (1, 0)
		h = Document.current_heading()
		self.assertEqual(h, None)

	def test_index_boundaries(self):
		# test index boundaries
		vim.current.window.cursor = (-1, 0)
		h = Document.current_heading()
		self.assertEqual(h, None)

		vim.current.window.cursor = (20, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

		vim.current.window.cursor = (999, 0)
		h = Document.current_heading()
		self.assertEqual(h, None)

	def test_heading_start_and_end(self):
		# test heading start and end
		vim.current.window.cursor = (2, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 1)
		self.assertEqual(h.end, 4)
		self.assertEqual(h.end_of_last_child, 15)

		vim.current.window.cursor = (11, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 9)
		self.assertEqual(h.end, 11)
		self.assertEqual(h.end_of_last_child, 15)

		vim.current.window.cursor = (18, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 17)
		self.assertEqual(h.end, 19)
		self.assertEqual(h.end_of_last_child, 19)

		vim.current.buffer = """
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		vim.current.window.cursor = (2, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.children[1].start, 7)
		self.assertEqual(h.children[1].children, [])
		self.assertEqual(h.children[1].next_sibling, None)
		self.assertEqual(h.children[1].end, 7)
		self.assertEqual(h.start, 1)
		self.assertEqual(h.end, 3)
		self.assertEqual(h.end_of_last_child, 7)

		vim.current.buffer = """
* Überschrift 2
* Überschrift 3""".split('\n')
		vim.current.window.cursor = (3, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.end, 2)
		self.assertEqual(h.end_of_last_child, 2)
		self.assertEqual(h.text, 'Überschrift 3')

	def test_first_heading(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		h = Document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.previous_sibling, None)

		self.assertEqual(h.children[0].level, 2)
		self.assertEqual(h.children[0].children, [])
		self.assertEqual(h.children[1].level, 2)
		self.assertEqual(len(h.children[1].children), 2)
		self.assertEqual(h.children[1].children[0].level, 4)
		self.assertEqual(h.children[1].children[1].level, 3)

		self.assertEqual(h.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.next_sibling, None)
		self.assertEqual(h.next_sibling.next_sibling.parent, None)

	def test_heading_in_the_middle(self):
		# test heading in the middle of the file
		vim.current.window.cursor = (14, 0)
		h = Document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 4)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.next_sibling, None)
		self.assertNotEqual(h.next_sibling.previous_sibling, None)
		self.assertEqual(h.next_sibling.level, 3)
		self.assertEqual(h.previous_sibling, None)

	def test_previous_headings(self):
		# test previous headings
		vim.current.window.cursor = (16, 0)
		h = Document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 3)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.parent.previous_sibling, None)
		self.assertNotEqual(h.previous_sibling.parent, None)
		self.assertEqual(h.previous_sibling.parent.start, 9)

		vim.current.window.cursor = (13, 0)
		h = Document.current_heading()
		self.assertNotEqual(h.parent, None)
		self.assertEqual(h.parent.start, 9)

		vim.current.window.cursor = (20, 0)
		h = Document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertNotEqual(h.previous_sibling.previous_sibling, None)
		self.assertEqual(h.previous_sibling.previous_sibling.level, 1)
		self.assertEqual(h.previous_sibling.previous_sibling.previous_sibling,
                None)

		vim.current.window.cursor = (77, 0)
		h = Document.current_heading()
		self.assertEqual(h, None)

		# test heading extractor
		#self.assertEqual(h.heading, 'Überschrift 1')
		#self.assertEqual(h.text, 'Text 1\n\nBla bla')

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(HeadingTestCase)
