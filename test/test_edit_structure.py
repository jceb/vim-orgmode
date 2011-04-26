# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import ORGMODE
from orgmode.liborgmode import Document


class EditStructureTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0}
		if not 'EditStructure' in ORGMODE.plugins:
			ORGMODE.register_plugin('EditStructure')
		self.editstructure = ORGMODE.plugins['EditStructure']
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

	def test_new_heading_below_normal_behavior(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.current.buffer[0], '* ')
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')

	def test_new_heading_above_normal_behavior(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.current.buffer[0], '* ')
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')

	def test_new_heading_below(self):
		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 6gg"|startinsert!')
		self.assertEqual(vim.current.buffer[4], 'Bla bla')
		self.assertEqual(vim.current.buffer[5], '* ')
		self.assertEqual(vim.current.buffer[6], '** Überschrift 1.1')

	def test_new_heading_below_in_the_middle(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 13gg"|startinsert!')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '** ')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')

	def test_new_heading_below_in_the_middle2(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 16gg"|startinsert!')
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '**** ')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')

	def test_new_heading_below_in_the_middle3(self):
		vim.current.window.cursor = (16, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 17gg"|startinsert!')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '*** ')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_at_the_end(self):
		vim.current.window.cursor = (18, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 21gg"|startinsert!')
		self.assertEqual(vim.current.buffer[19], '')
		self.assertEqual(vim.current.buffer[20], '* ')
		self.assertEqual(len(vim.current.buffer), 21)

	def test_new_heading_above(self):
		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 2gg"|startinsert!')
		self.assertEqual(vim.current.buffer[0], '')
		self.assertEqual(vim.current.buffer[1], '* ')
		self.assertEqual(vim.current.buffer[2], '* Überschrift 1')

	def test_new_heading_above_in_the_middle(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 10gg"|startinsert!')
		self.assertEqual(vim.current.buffer[8], 'Bla Bla bla')
		self.assertEqual(vim.current.buffer[9], '** ')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')

	def test_new_heading_above_in_the_middle2(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 13gg"|startinsert!')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '**** ')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')

	def test_new_heading_above_in_the_middle3(self):
		vim.current.window.cursor = (16, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 16gg"|startinsert!')
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** ')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')

	def test_new_heading_above_at_the_end(self):
		vim.current.window.cursor = (18, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 18gg"|startinsert!')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.buffer[17], '* ')
		self.assertEqual(vim.current.buffer[18], '* Überschrift 3')

	def test_promote_heading(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 13ggV15gg=')
		self.assertEqual(vim.current.buffer[10], 'Text 3')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '***** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[13], '')
		# actually the indentation comes through vim, just the heading is updated
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.window.cursor, (13, 1))

	def test_promote_last_heading(self):
		vim.current.buffer = """
* Überschrift 2
* Überschrift 3""".split('\n')
		vim.current.window.cursor = (3, 0)
		h = Document.current_heading()
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(h.end, 2)
		self.assertFalse(vim.CMDHISTORY)
		self.assertEqual(vim.current.buffer[2], '** Überschrift 3')
		self.assertEqual(vim.current.window.cursor, (3, 1))

	def test_demote_heading(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 13ggV15gg=')
		self.assertEqual(vim.current.buffer[10], 'Text 3')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '*** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[13], '')
		# actually the indentation comes through vim, just the heading is updated
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.window.cursor, (13, -1))

	def test_demote_level_one_heading(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(len(vim.CMDHISTORY), 0)
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_promote_parent_heading(self):
		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV16gg=')
		self.assertEqual(vim.current.buffer[1], '** Überschrift 1')
		self.assertEqual(vim.current.buffer[5], '*** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '*** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '***** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '**** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (2, 1))

	def test_demote_parent_heading(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10ggV16gg=')
		self.assertEqual(vim.current.buffer[5], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '* Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '*** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (10, -1))

	# run tests with count
	def test_promote_parent_heading_count(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = 3
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(len(vim.CMDHISTORY), 3)
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 2ggV16gg=')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 2ggV16gg=')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV16gg=')
		self.assertEqual(vim.current.buffer[1], '**** Überschrift 1')
		self.assertEqual(vim.current.buffer[5], '***** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '***** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '******* Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '****** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (2, 3))

	def test_demote_parent_heading(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS["v:count"] = 3
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(len(vim.CMDHISTORY), 3)
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 13ggV15gg=')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13ggV15gg=')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 13ggV16gg=')
		self.assertEqual(vim.current.buffer[5], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '* Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (13, -3))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(EditStructureTestCase)
