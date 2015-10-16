# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

counter = 0
class ShowHideTestCase(unittest.TestCase):
	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u'exists("b:org_todo_keywords")'.encode(u'utf-8'): '0'.encode(u'utf-8'),
				# global values for org_todo_keywords
				u'exists("g:org_todo_keywords")'.encode(u'utf-8'): '1'.encode(u'utf-8'),
				u'g:org_todo_keywords'.encode(u'utf-8'): [u'TODO'.encode(u'utf-8'), u'DONE'.encode(u'utf-8'), u'|'.encode(u'utf-8')],
				u'exists("g:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("*repeat#set()")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'b:changedtick'.encode(u'utf-8'): (u'%d' % counter).encode(u'utf-8'),
				u"v:count".encode(u'utf-8'): u'0'.encode(u'utf-8')}
		if not u'ShowHide' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'ShowHide')
		self.showhide = ORGMODE.plugins[u'ShowHide']
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
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
""".split(u'\n') ]

	def test_no_heading_toggle_folding(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.EVALHISTORY[-1], u'feedkeys("<Tab>", "n")'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (1, 0))

	def test_toggle_folding_first_heading_with_no_children(self):
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'2'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(7)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		vim.current.window.cursor = (2, 0)

		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 1zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_close_one(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u'13,15foldclose!'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 2zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 1zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'2,16foldclose!'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'2'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 1zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 6gg1zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 10gg1zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u'normal! 6gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-3], u'normal! 10gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u'normal! 6gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-3], u'normal! 10gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16gg2zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u'normal! 6gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-3], u'normal! 10gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u'normal! 6gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-3], u'normal! 10gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u'normal! 6gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-3], u'normal! 10gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16gg3zo'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_no_heading_toggle_folding_reverse(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.EVALHISTORY[-1], u'feedkeys("<Tab>", "n")'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (1, 0))

	def test_toggle_folding_first_heading_with_no_children_reverse(self):
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'2'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(7)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		vim.current.window.cursor = (2, 0)

		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u'2,5foldopen!'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_close_one_reverse(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 13ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one_reverse(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'10,16foldopen!'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u'normal! 13ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'2'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'2,16foldopen!'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 2ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'10'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 6ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 10ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'16'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 13ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u'foldclosed(2)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(6)'.encode(u'utf-8'): u'6'.encode(u'utf-8'),
				u'foldclosed(10)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				u'foldclosed(13)'.encode(u'utf-8'): u'13'.encode(u'utf-8'),
				u'foldclosed(16)'.encode(u'utf-8'): u'-1'.encode(u'utf-8'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'normal! 16ggzc'.encode(u'utf-8'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(ShowHideTestCase)
