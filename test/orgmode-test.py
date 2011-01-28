#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import indent_orgmode, fold_orgmode, ORGMODE
from orgmode.heading import Heading

ORGMODE.debug = True

START = True
END = False

def set_visual_selection(visualmode, line_start, line_end, col_start=1, col_end=1, cursor_pos=START):
	if visualmode not in ('', 'V', 'v'):
		raise ValueError('Illegal value for visualmode, must be in , V, v')

	vim.EVALRESULTS['visualmode()'] = visualmode

	# getpos results [bufnum, lnum, col, off]
	vim.EVALRESULTS['getpos("\'<")'] = ('', '%d' % line_start, '%d' % col_start, '')
	vim.EVALRESULTS['getpos("\'>")'] = ('', '%d' % line_end, '%d' % col_end, '')
	if cursor_pos == START:
		vim.current.window.cursor = (line_start, col_start)
	else:
		vim.current.window.cursor = (line_end, col_end)

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
				"v:count": 0
				}
		if not ORGMODE.plugins.has_key('TagsProperties'):
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

class ShowHideTestCase(unittest.TestCase):
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
				"v:count": 0
				}
		if not ORGMODE.plugins.has_key('ShowHide'):
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

	def test_toggle_folding_close_one(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS = {
				'foldclosed(13)': -1,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], '13,15foldclose!')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2zo')
		self.assertEqual(vim.current.window.cursor, (13, 0))

	def test_toggle_folding_open_one(self):
		vim.current.window.cursor = (10, 0)
		vim.EVALRESULTS = {
				'foldclosed(10)': 10,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1zo')
		self.assertEqual(vim.current.window.cursor, (10, 0))

	def test_toggle_folding_close_multiple_all_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				'foldclosed(2)': -1,
				'foldclosed(6)': -1,
				'foldclosed(10)': -1,
				'foldclosed(13)': -1,
				'foldclosed(16)': -1,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], '2,16foldclose!')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_all_closed(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				'foldclosed(2)': 2,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 0zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_first_level_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				'foldclosed(2)': -1,
				'foldclosed(6)': 6,
				'foldclosed(10)': 10,
				'foldclosed(13)': 13,
				'foldclosed(16)': 16,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 2)
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 6gg1zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10gg1zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_toggle_folding_open_multiple_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS = {
				'foldclosed(2)': -1,
				'foldclosed(6)': -1,
				'foldclosed(10)': 10,
				'foldclosed(13)': 13,
				'foldclosed(16)': 16,
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
				'foldclosed(2)': -1,
				'foldclosed(6)': 6,
				'foldclosed(10)': -1,
				'foldclosed(13)': 13,
				'foldclosed(16)': 16,
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
				'foldclosed(2)': -1,
				'foldclosed(6)': -1,
				'foldclosed(10)': -1,
				'foldclosed(13)': -1,
				'foldclosed(16)': 16,
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
				'foldclosed(2)': -1,
				'foldclosed(6)': -1,
				'foldclosed(10)': -1,
				'foldclosed(13)': 13,
				'foldclosed(16)': -1,
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
				'foldclosed(2)': -1,
				'foldclosed(6)': 6,
				'foldclosed(10)': -1,
				'foldclosed(13)': 13,
				'foldclosed(16)': -1,
				}
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(len(vim.CMDHISTORY), 4)
		self.assertEqual(vim.CMDHISTORY[-4], 'normal 6gg3zo')
		self.assertEqual(vim.CMDHISTORY[-3], 'normal 10gg3zo')
		self.assertEqual(vim.CMDHISTORY[-2], 'normal 13gg3zo')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16gg3zo')
		self.assertEqual(vim.current.window.cursor, (2, 0))

class EditStructureTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0
				}
		if not ORGMODE.plugins.has_key('EditStructure'):
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

class NavigatorTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0,
				}
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

		if not ORGMODE.plugins.has_key('Navigator'):
			ORGMODE.register_plugin('Navigator')
		self.navigator = ORGMODE.plugins['Navigator']

	def test_movement(self):
		# test movement outside any heading
		vim.current.window.cursor = (0, 0)
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (0, 0))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_forward_movement(self):
		# test forward movement
		vim.current.window.cursor = (2, 0)
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (13, 5))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (17, 2))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		## don't move cursor if last heading is already focussed
		vim.current.window.cursor = (19, 6)
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (19, 6))

		## test movement with count
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = 1
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.next(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		vim.EVALRESULTS["v:count"] = 0

	def test_backward_movement(self):
		# test backward movement
		vim.current.window.cursor = (19, 6)
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (17, 2))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (13, 5))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		## test movement with count
		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		vim.EVALRESULTS["v:count"] = 4
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))
		vim.EVALRESULTS["v:count"] = 4
		self.navigator.previous(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_parent_movement(self):
		# test movement to parent
		vim.current.window.cursor = (2, 0)
		self.assertEqual(self.navigator.parent(mode='normal'), None)
		self.assertEqual(vim.current.window.cursor, (2, 0))

		vim.current.window.cursor = (3, 4)
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (3, 4))

		vim.current.window.cursor = (16, 4)
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		vim.current.window.cursor = (15, 6)
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		## test movement with count
		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = -1
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 0
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 1
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 2
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS["v:count"] = 3
		self.navigator.parent(mode='normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_forward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |

		# << text
		# text| >>
		# text
		# heading
		set_visual_selection('V', 2, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5gg')

		# << text
		# text
		# text| >>
		# heading
		set_visual_selection('V', 2, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV9gg')

		# << text
		# x. heading
		# text| >>
		# heading
		set_visual_selection('V', 12, 14, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV15gg')

		set_visual_selection('V', 12, 15, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV16gg')

		set_visual_selection('V', 12, 16, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV17gg')

		# << text
		# text
		# text| >>
		# heading
		# EOF
		set_visual_selection('V', 15, 17, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV20gg')

		# << text >>
		# heading
		set_visual_selection('V', 1, 1, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		# << heading >>
		# text
		# heading
		set_visual_selection('V', 2, 2, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5gg')

		# << text >>
		# heading
		set_visual_selection('V', 1, 1, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 1ggV5gg')

		# << |text
		# heading
		# text
		# heading
		# text >>
		set_visual_selection('V', 1, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# << |heading
		# text
		# heading
		# text >>
		set_visual_selection('V', 2, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 6ggV8ggo')

		# << |heading
		# text >>
		# heading
		set_visual_selection('V', 6, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 8ggV9gg')

		# << |x. heading
		# text >>
		# heading
		set_visual_selection('V', 13, 15, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV15gg')

		set_visual_selection('V', 13, 16, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV16ggo')

		set_visual_selection('V', 16, 16, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 16ggV17gg')

		# << |x. heading
		# text >>
		# heading
		# EOF
		set_visual_selection('V', 17, 17, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 17ggV20gg')

		# << |heading
		# text>>
		# text
		# EOF
		set_visual_selection('V', 18, 19, cursor_pos=START)
		self.assertEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 19ggV20gg')

		# << heading
		# text|>>
		# text
		# EOF
		set_visual_selection('V', 18, 19, cursor_pos=END)
		self.assertEqual(self.navigator.next(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 18ggV20gg')

		# << heading
		# text|>>
		# EOF
		set_visual_selection('V', 18, 20, cursor_pos=END)
		self.assertEqual(self.navigator.next(mode='visual'), None)

		# << |heading
		# text>>
		# EOF
		set_visual_selection('V', 20, 20, cursor_pos=START)
		self.assertEqual(self.navigator.next(mode='visual'), None)

	def test_backward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |

		# << text | >>
		# text
		# heading
		set_visual_selection('V', 1, 1, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal gv')

		set_visual_selection('V', 1, 1, cursor_pos=END)
		self.assertEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal gv')

		# << heading| >>
		# text
		# heading
		set_visual_selection('V', 2, 2, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV2ggo')

		set_visual_selection('V', 2, 2, cursor_pos=END)
		self.assertEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV2ggo')

		# heading
		# text
		# << |text
		# text >>
		set_visual_selection('V', 3, 5, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5ggo')

		# heading
		# text
		# << text
		# text| >>
		set_visual_selection('V', 3, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV3ggo')

		# heading
		# text
		# << text
		# text| >>
		set_visual_selection('V', 8, 9, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 6ggV8ggo')

		# heading
		# << text
		# x. heading
		# text| >>
		set_visual_selection('V', 12, 14, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV12gg')

		set_visual_selection('V', 12, 15, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV12gg')

		# heading
		# << |text
		# x. heading
		# text >>
		set_visual_selection('V', 12, 15, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10ggV15ggo')

		# heading
		# << text
		# x. heading| >>
		set_visual_selection('V', 12, 13, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV12gg')

		# heading
		# << text
		# heading
		# text
		# x. heading| >>
		set_visual_selection('V', 12, 16, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 12ggV15gg')

		# << text
		# heading
		# text
		# heading| >>
		set_visual_selection('V', 15, 17, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 15ggV16gg')

		# heading
		# << |text
		# text
		# heading
		# text >>
		set_visual_selection('V', 4, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# heading
		# << text
		# text
		# heading
		# text| >>
		set_visual_selection('V', 4, 8, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 4ggV5gg')

		# heading
		# << text
		# text
		# heading
		# text| >>
		set_visual_selection('V', 4, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV4ggo')

		# BOF
		# << |heading
		# text
		# heading
		# text >>
		set_visual_selection('V', 2, 8, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# BOF
		# heading
		# << text
		# text| >>
		set_visual_selection('V', 3, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV3ggo')

		# BOF
		# << heading
		# text
		# text| >>
		set_visual_selection('V', 2, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode='visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV2ggo')

		# << text
		# heading
		# text
		# x. heading
		# text| >>
		set_visual_selection('V', 8, 14, cursor_pos=END)
		self.navigator.previous(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 8ggV12gg')

	def test_parent_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor poistion: |

		# heading
		# << text|
		# text
		# text >>
		set_visual_selection('V', 4, 8, cursor_pos=START)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal gv')

		# heading
		# << text|
		# text
		# text >>
		set_visual_selection('V', 6, 8, cursor_pos=START)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# heading
		# << text
		# text
		# text| >>
		set_visual_selection('V', 6, 8, cursor_pos=END)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV6ggo')

		# << |heading
		# text
		# text
		# text >>
		set_visual_selection('V', 2, 8, cursor_pos=START)
		self.assertEqual(self.navigator.parent(mode='visual'), None)

		# << heading
		# text
		# heading
		# text| >>
		set_visual_selection('V', 2, 8, cursor_pos=END)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV5gg')

		set_visual_selection('V', 7, 8, cursor_pos=START)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV8ggo')

		# heading
		# heading
		# << text
		# text| >>
		set_visual_selection('V', 12, 13, cursor_pos=END)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10ggV12ggo')

		set_visual_selection('V', 10, 12, cursor_pos=START)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV12ggo')

		# heading
		# << text
		# text
		# heading| >>
		set_visual_selection('V', 11, 17, cursor_pos=END)
		self.assertEqual(self.navigator.parent(mode='visual'), None)

		# << text
		# heading
		# text
		# x. heading
		# text| >>
		set_visual_selection('V', 8, 14, cursor_pos=END)
		self.navigator.parent(mode='visual')
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 8ggV12gg')

class HeadingTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0
				}
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
		h = Heading.current_heading()
		self.assertEqual(h, None)

	def test_index_boundaries(self):
		# test index boundaries
		vim.current.window.cursor = (-1, 0)
		h = Heading.current_heading()
		self.assertEqual(h, None)

		vim.current.window.cursor = (999, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

	def test_heading_start_and_end(self):
		# test heading start and end
		vim.current.window.cursor = (2, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 1)
		self.assertEqual(h.end, 4)
		self.assertEqual(h.end_of_last_child, 15)

		vim.current.window.cursor = (11, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 9)
		self.assertEqual(h.end, 11)
		self.assertEqual(h.end_of_last_child, 15)

		vim.current.window.cursor = (18, 0)
		h = Heading.current_heading()
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
		h = Heading.current_heading()
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

	def test_first_heading(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		h = Heading.current_heading()

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
		h = Heading.current_heading()

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
		h = Heading.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 3)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.parent.previous_sibling, None)
		self.assertNotEqual(h.previous_sibling.parent, None)
		self.assertEqual(h.previous_sibling.parent.start, 9)

		vim.current.window.cursor = (13, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h.parent, None)
		self.assertEqual(h.parent.start, 9)

		vim.current.window.cursor = (77, 0)
		h = Heading.current_heading()

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

class MiscTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0,
				"v:lnum": 0
				}
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

	def test_indent_noheading(self):
		# test first heading
		vim.current.window.cursor = (1, 0)
		vim.EVALRESULTS['v:lnum'] = 1
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS['v:lnum'] = 2
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS['v:lnum'] = 3
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:indent_level = 2')

	def test_indent_heading_middle2(self):
		# test first heading
		vim.current.window.cursor = (4, 0)
		vim.EVALRESULTS['v:lnum'] = 4
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:indent_level = 2')

	def test_indent_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS['v:lnum'] = 5
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:indent_level = 2')

	def test_fold_heading_start(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS['v:lnum'] = 2
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = ">1"')

	def test_fold_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS['v:lnum'] = 3
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = 1')

	def test_fold_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS['v:lnum'] = 5
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = 1')

	def test_fold_heading_end_of_last_child(self):
		# test first heading
		vim.current.window.cursor = (16, 0)
		vim.EVALRESULTS['v:lnum'] = 16
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		# which is also end of the parent heading <1
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = ">3"')

	def test_fold_heading_end_of_last_child_next_heading(self):
		# test first heading
		vim.current.window.cursor = (17, 0)
		vim.EVALRESULTS['v:lnum'] = 17
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = ">1"')

	def test_fold_middle_subheading(self):
		# test first heading
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS['v:lnum'] = 13
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = ">4"')

	def test_fold_middle_subheading2(self):
		# test first heading
		vim.current.window.cursor = (14, 0)
		vim.EVALRESULTS['v:lnum'] = 14
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = 4')

	def test_fold_middle_subheading3(self):
		# test first heading
		vim.current.window.cursor = (15, 0)
		vim.EVALRESULTS['v:lnum'] = 15
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], 'let b:fold_expr = 4')

if __name__ == '__main__':
	unittest.main()
	#tests = unittest.TestSuite()
	#tests.addTest(HeadingTestCase())
	#tests.addTest(NavigatorTestCase())
	#tests.run()
