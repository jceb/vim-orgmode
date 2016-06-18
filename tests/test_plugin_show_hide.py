# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

from orgmode.py3compat.encode_compatibility import *

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
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONE')],
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("b:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u"v:count"): u_encode(u'0')}
		if not u'ShowHide' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'ShowHide')
		self.showhide = ORGMODE.plugins[u'ShowHide']
		vim.current.buffer[:] = [ u_encode(i) for i in u"""
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
		self.assertEqual(vim.EVALHISTORY[-1], u_encode(u'feedkeys("<Tab>", "n")'))
		self.assertEqual(vim.current.window.cursor, (1, 0))

	def test_toggle_folding_first_heading_with_no_children(self):
		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'2'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(7)'): u_encode(u'-1'),
				})
		vim.current.window.cursor = (2, 0)

		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_close_one(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'13,15foldclose!'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2zo'))
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,16foldclose!'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'2'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 6gg1zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 10gg1zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg2zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg2zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_no_heading_toggle_folding_reverse(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.EVALHISTORY[-1], u_encode(u'feedkeys("<Tab>", "n")'))
		self.assertEqual(vim.current.window.cursor, (1, 0))

	def test_toggle_folding_first_heading_with_no_children_reverse(self):
		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'2'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(7)'): u_encode(u'-1'),
				})
		vim.current.window.cursor = (2, 0)

		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,5foldopen!'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_close_one_reverse(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one_reverse(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'10,16foldopen!'))
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'2'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,16foldopen!'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'10'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 6ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 10ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'-1'),
				u_encode(u'foldclosed(16)'): u_encode(u'16'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'-1'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS.update({
				u_encode(u'foldclosed(2)'): u_encode(u'-1'),
				u_encode(u'foldclosed(6)'): u_encode(u'6'),
				u_encode(u'foldclosed(10)'): u_encode(u'-1'),
				u_encode(u'foldclosed(13)'): u_encode(u'13'),
				u_encode(u'foldclosed(16)'): u_encode(u'-1'),
				})
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, (2, 0))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(ShowHideTestCase)
