# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode import ORGMODE

counter = 0
class EditStructureTestCase(unittest.TestCase):
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
				u'exists("g:org_improve_split_heading")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_improve_split_heading")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("g:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_debug")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("*repeat#set()")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'b:changedtick'.encode(u'utf-8'): (u'%d' % counter).encode(u'utf-8'),
				u'&ts'.encode(u'utf-8'): u'8'.encode(u'utf-8'),
				u'exists("g:org_tag_column")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u'exists("b:org_tag_column")'.encode(u'utf-8'): u'0'.encode(u'utf-8'),
				u"v:count".encode(u'utf-8'): u'0'.encode(u'utf-8')}
		if not u'EditStructure' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'EditStructure')
		self.editstructure = ORGMODE.plugins[u'EditStructure']
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
""".split(u'\n')]

	def test_new_heading_below_normal_behavior(self):
		vim.current.window.cursor = (1, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True), None)
		self.assertEqual(vim.current.buffer[0], '* ')
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')

	def test_new_heading_above_normal_behavior(self):
		vim.current.window.cursor = (1, 1)
		self.assertNotEqual(self.editstructure.new_heading(below=False), None)
		self.assertEqual(vim.current.buffer[0], '* ')
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')

	def test_new_heading_below(self):
		vim.current.window.cursor = (2, 0)
		vim.current.buffer[5] = u'** Überschrift 1.1 :Tag:'
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=False), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 6gg"|startinsert!')
		self.assertEqual(vim.current.buffer[4], 'Bla bla')
		self.assertEqual(vim.current.buffer[5], '* ')
		self.assertEqual(vim.current.buffer[6], '** Überschrift 1.1							:Tag:')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_insert_mode(self):
		vim.current.window.cursor = (2, 1)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 3gg"|startinsert!')
		self.assertEqual(vim.current.buffer[2], '* Überschrift 1')
		self.assertEqual(vim.current.buffer[5], 'Bla bla')
		self.assertEqual(vim.current.buffer[6], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_split_text_at_the_end(self):
		vim.current.buffer[1] = u'* Überschriftx1'
		vim.current.window.cursor = (2, 14)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 3gg"|startinsert!')
		self.assertEqual(vim.current.buffer[2], '* ')
		self.assertEqual(vim.current.buffer[5], 'Bla bla')
		self.assertEqual(vim.current.buffer[6], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_split_text_at_the_end_insert_parts(self):
		vim.current.window.cursor = (2, 14)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 3gg"|startinsert!')
		self.assertEqual(vim.current.buffer[2], '* 1')
		self.assertEqual(vim.current.buffer[5], 'Bla bla')
		self.assertEqual(vim.current.buffer[6], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_in_the_middle(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 13gg"|startinsert!')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '** ')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')

	def test_new_heading_below_in_the_middle2(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 16gg"|startinsert!')
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '**** ')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')

	def test_new_heading_below_in_the_middle3(self):
		vim.current.window.cursor = (16, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 17gg"|startinsert!')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '*** ')
		self.assertEqual(vim.current.buffer[17], '* Überschrift 2')

	def test_new_heading_below_at_the_end(self):
		vim.current.window.cursor = (18, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=True, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 21gg"|startinsert!')
		self.assertEqual(vim.current.buffer[19], '')
		self.assertEqual(vim.current.buffer[20], '* ')
		self.assertEqual(len(vim.current.buffer), 21)

	def test_new_heading_above(self):
		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 2gg"|startinsert!')
		self.assertEqual(vim.current.buffer[0], '')
		self.assertEqual(vim.current.buffer[1], '* ')
		self.assertEqual(vim.current.buffer[2], '* Überschrift 1')

	def test_new_heading_above_in_the_middle(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 10gg"|startinsert!')
		self.assertEqual(vim.current.buffer[8], 'Bla Bla bla')
		self.assertEqual(vim.current.buffer[9], '** ')
		self.assertEqual(vim.current.buffer[10], '** Überschrift 1.2')

	def test_new_heading_above_in_the_middle2(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 13gg"|startinsert!')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '**** ')
		self.assertEqual(vim.current.buffer[13], '**** Überschrift 1.2.1.falsch')

	def test_new_heading_above_in_the_middle3(self):
		vim.current.window.cursor = (16, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 16gg"|startinsert!')
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** ')
		self.assertEqual(vim.current.buffer[16], '*** Überschrift 1.2.1')

	def test_new_heading_above_at_the_end(self):
		vim.current.window.cursor = (18, 0)
		self.assertNotEqual(self.editstructure.new_heading(below=False, insert_mode=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'exe "normal 18gg"|startinsert!')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.buffer[17], '* ')
		self.assertEqual(vim.current.buffer[18], '* Überschrift 3')

	def test_new_heading_below_split_heading_title(self):
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* Überschrift 1  :Tag:
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
""".split(u'\n')]
		vim.current.window.cursor = (2, 6)
		self.assertNotEqual(self.editstructure.new_heading(insert_mode=True), None)
		self.assertEqual(vim.current.buffer[0], '')
		self.assertEqual(vim.current.buffer[1], '* Über									:Tag:')
		self.assertEqual(vim.current.buffer[2], '* schrift 1')
		self.assertEqual(vim.current.buffer[3], 'Text 1')

	def test_new_heading_below_split_heading_title_with_todo(self):
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* TODO Überschrift 1  :Tag:
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
""".split(u'\n')]
		vim.current.window.cursor = (2, 5)
		self.assertNotEqual(self.editstructure.new_heading(insert_mode=True), None)
		self.assertEqual(vim.current.buffer[0], '')
		self.assertEqual(vim.current.buffer[1], '* TODO									:Tag:')
		self.assertEqual(vim.current.buffer[2], '* Überschrift 1')
		self.assertEqual(vim.current.buffer[3], 'Text 1')

	def test_demote_heading(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 13ggV15gg=')
		self.assertEqual(vim.current.buffer[10], 'Text 3')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '***** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[13], '')
		# actually the indentation comes through vim, just the heading is updated
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.window.cursor, (13, 1))

	def test_demote_last_heading(self):
		vim.current.buffer[:] = """
* Überschrift 2
* Überschrift 3""".split('\n')
		vim.current.window.cursor = (3, 0)
		h = ORGMODE.get_document().current_heading()
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(h.end, 2)
		self.assertFalse(vim.CMDHISTORY)
		self.assertEqual(vim.current.buffer[2], '** Überschrift 3')
		self.assertEqual(vim.current.window.cursor, (3, 1))

	def test_promote_heading(self):
		vim.current.window.cursor = (13, 0)
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 13ggV15gg=')
		self.assertEqual(vim.current.buffer[10], 'Text 3')
		self.assertEqual(vim.current.buffer[11], '')
		self.assertEqual(vim.current.buffer[12], '*** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[13], '')
		# actually the indentation comes through vim, just the heading is updated
		self.assertEqual(vim.current.buffer[14], 'Bla Bla bla bla')
		self.assertEqual(vim.current.buffer[15], '*** Überschrift 1.2.1')
		self.assertEqual(vim.current.window.cursor, (13, -1))

	def test_promote_level_one_heading(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(len(vim.CMDHISTORY), 0)
		self.assertEqual(vim.current.buffer[1], '* Überschrift 1')
		self.assertEqual(vim.current.window.cursor, (2, 0))

	def test_demote_parent_heading(self):
		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.editstructure.demote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 2ggV16gg=')
		self.assertEqual(vim.current.buffer[1], '** Überschrift 1')
		self.assertEqual(vim.current.buffer[5], '*** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '*** Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '***** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '**** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (2, 1))

	def test_promote_parent_heading(self):
		vim.current.window.cursor = (10, 0)
		self.assertNotEqual(self.editstructure.promote_heading(), None)
		self.assertEqual(vim.CMDHISTORY[-1], 'normal 10ggV16gg=')
		self.assertEqual(vim.current.buffer[5], '** Überschrift 1.1')
		self.assertEqual(vim.current.buffer[9], '* Überschrift 1.2')
		self.assertEqual(vim.current.buffer[12], '*** Überschrift 1.2.1.falsch')
		self.assertEqual(vim.current.buffer[15], '** Überschrift 1.2.1')
		self.assertEqual(vim.current.buffer[16], '* Überschrift 2')
		self.assertEqual(vim.current.window.cursor, (10, -1))

	# run tests with count
	def test_demote_parent_heading_count(self):
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS["v:count"] = '3'
		self.assertNotEqual(self.editstructure.demote_heading(), None)
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

	def test_promote_parent_heading(self):
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS["v:count"] = '3'
		self.assertNotEqual(self.editstructure.promote_heading(), None)
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
