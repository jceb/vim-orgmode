#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode import indent_orgmode, fold_orgmode, ORGMODE
from orgmode.heading import Heading


ORGMODE.start()
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

	def test_promote_last_heading(self):
		vim.current.buffer = """
* Überschrift 2
* Überschrift 3""".split('\n')
		vim.current.window.cursor = (3, 0)
		h = Heading.current_heading()
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

		vim.current.window.cursor = (20, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

		vim.current.window.cursor = (999, 0)
		h = Heading.current_heading()
		self.assertEqual(h, None)

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

		vim.current.buffer = """
* Überschrift 2
* Überschrift 3""".split('\n')
		vim.current.window.cursor = (3, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.end, 2)
		self.assertEqual(h.end_of_last_child, 2)
		self.assertEqual(h.text, 'Überschrift 3')

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

		vim.current.window.cursor = (20, 0)
		h = Heading.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertNotEqual(h.previous_sibling.previous_sibling, None)
		self.assertEqual(h.previous_sibling.previous_sibling.level, 1)
		self.assertEqual(h.previous_sibling.previous_sibling.previous_sibling, None)

		vim.current.window.cursor = (77, 0)
		h = Heading.current_heading()
		self.assertEqual(h, None)

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
