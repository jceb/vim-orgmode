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
class TagsPropertiesTestCase(unittest.TestCase):
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
		if not u'TagsProperties' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'TagsProperties')
		self.showhide = ORGMODE.plugins[u'TagsProperties']
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

	def test_new_property(self):
		u""" TODO: Docstring for test_new_property

		:returns: TODO
		u"""
		pass

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TagsPropertiesTestCase)
