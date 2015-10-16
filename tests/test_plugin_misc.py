#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import indent_orgmode, fold_orgmode, ORGMODE

ORGMODE.debug = True

START = True
END = False

counter = 0
class MiscTestCase(unittest.TestCase):
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
				u'exists("g:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("*repeat#set()")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u"v:count".encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'b:changedtick'.encode(u'utf-8'): (u'%d' % counter).encode(u'utf-8'),
				u"v:lnum".encode(u'utf-8'): u'0'.encode(u'utf-8')}
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

	def test_indent_noheading(self):
		# test first heading
		vim.current.window.cursor = (1, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'1'.encode(u'utf-8')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'2'.encode(u'utf-8')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'3'.encode(u'utf-8')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:indent_level = 2'.encode(u'utf-8'))

	def test_indent_heading_middle2(self):
		# test first heading
		vim.current.window.cursor = (4, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'4'.encode(u'utf-8')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:indent_level = 2'.encode(u'utf-8'))

	def test_indent_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'5'.encode(u'utf-8')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:indent_level = 2'.encode(u'utf-8'))

	def test_fold_heading_start(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'2'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = ">1"'.encode(u'utf-8'))

	def test_fold_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'3'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = 1'.encode(u'utf-8'))

	def test_fold_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'5'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = 1'.encode(u'utf-8'))

	def test_fold_heading_end_of_last_child(self):
		# test first heading
		vim.current.window.cursor = (16, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'16'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		# which is also end of the parent heading <1
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = ">3"'.encode(u'utf-8'))

	def test_fold_heading_end_of_last_child_next_heading(self):
		# test first heading
		vim.current.window.cursor = (17, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'17'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = ">1"'.encode(u'utf-8'))

	def test_fold_middle_subheading(self):
		# test first heading
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'13'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = ">4"'.encode(u'utf-8'))

	def test_fold_middle_subheading2(self):
		# test first heading
		vim.current.window.cursor = (14, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'14'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = 4'.encode(u'utf-8'))

	def test_fold_middle_subheading3(self):
		# test first heading
		vim.current.window.cursor = (15, 0)
		vim.EVALRESULTS[u'v:lnum'.encode(u'utf-8')] = u'15'.encode(u'utf-8')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u'let b:fold_expr = 4'.encode(u'utf-8'))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(MiscTestCase)
