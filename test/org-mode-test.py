#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		vim.EVALRESULTS = {
				'exists("g:orgmode_plugins")': True,
				"g:orgmode_plugins": ['Todo']
				}

	def test_heading_structure_normal(self):
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
""".split('\n')
		self.run_tests(True)

	def test_heading_structure_indent(self):
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
 * Überschrift 1.1
Text 2

Bla Bla bla
 * Überschrift 1.2
Text 3

   * Überschrift 1.2.1.falsch

Bla Bla bla bla
  * Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
""".split('\n')
		self.run_tests(False)


	def run_tests(self, mode=False):
		from orgmode import Heading

		# test no heading
		vim.current.window.cursor = (1, 0)
		h = Heading.current_heading(mode)
		self.assertEqual(h, None)

		# test index boundaries
		vim.current.window.cursor = (-1, 0)
		h = Heading.current_heading(mode)
		self.assertEqual(h, None)

		vim.current.window.cursor = (999, 0)
		h = Heading.current_heading(mode)
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

		# test first heading
		vim.current.window.cursor = (2, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.previous_sibling, None)

		self.assertEqual(h.children[0].level, 2)
		self.assertEqual(h.children[1].level, 2)
		self.assertEqual(len(h.children[1].children), 2)
		self.assertEqual(h.children[1].children[0].level, 4)
		self.assertEqual(h.children[1].children[1].level, 3)

		self.assertEqual(h.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.next_sibling, None)
		self.assertEqual(h.next_sibling.next_sibling.parent, None)

		# test heading in the middle of the file
		vim.current.window.cursor = (14, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 4)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.next_sibling, None)
		self.assertNotEqual(h.next_sibling.previous_sibling, None)
		self.assertEqual(h.next_sibling.level, 3)
		self.assertEqual(h.previous_sibling, None)

		#self.assertEqual(h.heading, 'Überschrift 1')
		#self.assertEqual(h.text, 'Text 1\n\nBla bla')

if __name__ == '__main__':
	unittest.main()
