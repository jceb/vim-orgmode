#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import ORGMODE, Heading

ORGMODE.debug = True

class TestSequenceFunctions(unittest.TestCase):

	def setUp(self):
		vim.EVALRESULTS = {
				'exists("g:orgmode_plugins")': True,
				"g:orgmode_plugins": ['Todo']
				}

	def test_navigator(self):
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

		ORGMODE.register_plugin('Navigator')
		navigator = ORGMODE.plugins['Navigator']

		vim.current.window.cursor = (0, 0)
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (0, 0))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (2, 3))

		# test forward movement
		vim.current.window.cursor = (2, 0)
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (6, 4))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (13, 6))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (17, 3))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (18, 3))

		# don't move cursor if last heading is already focussed
		vim.current.window.cursor = (19, 6)
		navigator.next()
		self.assertEqual(vim.current.window.cursor, (19, 6))

		# test backward movement
		vim.current.window.cursor = (19, 6)
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (17, 3))
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (16, 5))
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (13, 6))
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (10, 4))
		navigator.previous()
		self.assertEqual(vim.current.window.cursor, (6, 4))
		navigator.previous()
		vim.current.window.cursor = (2, 0)

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
		self.run_heading_tests(True)

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
		self.run_heading_tests(False)


	def run_heading_tests(self, mode=False):

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
		self.assertEqual(h.children[0].children, [])
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

		# test previous headings
		vim.current.window.cursor = (16, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 3)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.parent.previous_sibling, None)
		self.assertNotEqual(h.previous_sibling.parent, None)
		self.assertEqual(h.previous_sibling.parent.start, 9)

		vim.current.window.cursor = (13, 0)
		h = Heading.current_heading(mode)
		self.assertNotEqual(h.parent, None)
		self.assertEqual(h.parent.start, 9)

		vim.current.window.cursor = (77, 0)
		h = Heading.current_heading(mode)

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertNotEqual(h.previous_sibling.previous_sibling, None)
		self.assertEqual(h.previous_sibling.previous_sibling.level, 1)
		self.assertEqual(h.previous_sibling.previous_sibling.previous_sibling, None)

		# test heading extractor
		#self.assertEqual(h.heading, 'Überschrift 1')
		#self.assertEqual(h.text, 'Text 1\n\nBla bla')


if __name__ == '__main__':
	unittest.main()
