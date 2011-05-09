# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode import ORGMODE

class ShowHideTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				u'exists("g:org_debug")': 0,
				u'exists("b:org_debug")': 0,
				u'exists("*repeat#set()")': 0,
				u'exists("b:org_leader")': 0,
				u'exists("g:org_leader")': 0,
				u'b:changedtick': 0,
				u"v:count": 0}
		if not 'ShowHide' in ORGMODE.plugins:
			ORGMODE.register_plugin('ShowHide')
		self.showhide = ORGMODE.plugins['ShowHide']
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

	def test_no_heading_toggle_folding(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.EVALHISTORY[-1], 'feedkeys("<Tab>", "n")')
		self.assertEqual(vim.current.window.cursor, (1, 0))

	def test_toggle_folding_first_heading_with_no_children(self):
		vim.current.buffer = """
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		vim.EVALRESULTS = {
				u'foldclosed(2)': 2,
				u'foldclosed(6)': -1,
				u'foldclosed(7)': -1,
				u'b:changedtick': 0,
				}
		vim.current.window.cursor = (2, 0)

		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_close_one(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS = {
				u'foldclosed(13)': -1,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], '13,15foldclose!')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2zo')
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS = {
				u'foldclosed(10)': 10,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1zo')
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': -1,
				u'foldclosed(10)': -1,
				u'foldclosed(13)': -1,
				u'foldclosed(16)': -1,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], '2,16foldclose!')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': 2,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': 6,
				u'foldclosed(10)': 10,
				u'foldclosed(13)': 13,
				u'foldclosed(16)': 16,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 6gg1zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10gg1zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': -1,
				u'foldclosed(10)': 10,
				u'foldclosed(13)': 13,
				u'foldclosed(16)': 16,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg2zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg2zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg2zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg2zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': 6,
				u'foldclosed(10)': -1,
				u'foldclosed(13)': 13,
				u'foldclosed(16)': 16,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg2zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg2zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg2zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg2zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': -1,
				u'foldclosed(10)': -1,
				u'foldclosed(13)': -1,
				u'foldclosed(16)': 16,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg3zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg3zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg3zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg3zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': -1,
				u'foldclosed(10)': -1,
				u'foldclosed(13)': 13,
				u'foldclosed(16)': -1,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg3zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg3zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg3zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg3zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				u'foldclosed(2)': -1,
				u'foldclosed(6)': 6,
				u'foldclosed(10)': -1,
				u'foldclosed(13)': 13,
				u'foldclosed(16)': -1,
				u'b:changedtick': 0,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg3zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg3zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg3zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg3zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(ShowHideTestCase)
