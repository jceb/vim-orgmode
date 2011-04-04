#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import indent_orgmode, fold_orgmode, ORGMODE

ORGMODE.debug = True

START = True
END = False

class TagsPropertiesTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("b:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				'exists("b:org_leader")': 0,
				'exists("g:org_leader")': 0,
				'exists("g:org_tags_column")': 0,
				'exists("b:org_tags_column")': 0,
				'exists("b:org_tags_completion_ignorecase")': 0,
				'exists("g:org_tags_completion_ignorecase")': 0,
				"v:count": 0}
		if not 'TagsProperties' in ORGMODE.plugins:
			ORGMODE.register_plugin('TagsProperties')
		self.showhide = ORGMODE.plugins['TagsProperties']
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

	def test_new_property(self):
		""" TODO: Docstring for test_new_property

		:returns: TODO
		"""
		pass

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TagsPropertiesTestCase)
