# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode._vim import ORGMODE

from orgmode.py3compat.encode_compatibility import *

START = True
END = False

def set_visual_selection(visualmode, line_start, line_end, col_start=1,
        col_end=1, cursor_pos=START):

	if visualmode not in (u'', u'V', u'v'):
		raise ValueError(u'Illegal value for visualmode, must be in , V, v')

	vim.EVALRESULTS['visualmode()'] = visualmode

	# getpos results [bufnum, lnum, col, off]
	vim.EVALRESULTS['getpos("\'<")'] = ('', '%d' % line_start, '%d' %
			col_start, '')
	vim.EVALRESULTS['getpos("\'>")'] = ('', '%d' % line_end, '%d' %
			col_end, '')
	if cursor_pos == START:
		vim.current.window.cursor = (line_start, col_start)
	else:
		vim.current.window.cursor = (line_end, col_end)


counter = 0
class NavigatorTestCase(unittest.TestCase):
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
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u"v:count"): u_encode(u'0'),
				}
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

		if not u'Navigator' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'Navigator')
		self.navigator = ORGMODE.plugins[u'Navigator']

	def test_movement(self):
		# test movement outside any heading
		vim.current.window.cursor = (1, 0)
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (1, 0))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_forward_movement(self):
		# test forward movement
		vim.current.window.cursor = (2, 0)
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (13, 5))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (17, 2))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		## don't move cursor if last heading is already focussed
		vim.current.window.cursor = (19, 6)
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (19, 6))

		## test movement with count
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'-1')
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'0')
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))

		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'1')
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'3')
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.next(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'0')

	def test_backward_movement(self):
		# test backward movement
		vim.current.window.cursor = (19, 6)
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (17, 2))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (13, 5))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (6, 3))
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		## test movement with count
		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'-1')
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'0')
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (18, 2))

		vim.current.window.cursor = (19, 6)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'3')
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (16, 4))
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'4')
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'4')
		self.navigator.previous(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_parent_movement(self):
		# test movement to parent
		vim.current.window.cursor = (2, 0)
		self.assertEqual(self.navigator.parent(mode=u'normal'), None)
		self.assertEqual(vim.current.window.cursor, (2, 0))

		vim.current.window.cursor = (3, 4)
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (3, 4))

		vim.current.window.cursor = (16, 4)
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		vim.current.window.cursor = (15, 6)
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		## test movement with count
		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'-1')
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'0')
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'1')
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (10, 3))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'2')
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

		vim.current.window.cursor = (16, 4)
		vim.EVALRESULTS[u_encode(u"v:count")] = u_encode(u'3')
		self.navigator.parent(mode=u'normal')
		self.assertEqual(vim.current.window.cursor, (2, 2))

	def test_next_parent_movement(self):
		# test movement to parent
		vim.current.window.cursor = (6, 0)
		self.assertNotEqual(self.navigator.parent_next_sibling(mode=u'normal'), None)
		self.assertEqual(vim.current.window.cursor, (17, 2))

	def test_forward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor position: |

		# << text
		# text| >>
		# text
		# heading
		set_visual_selection(u'V', 2, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV5gg'))

		# << text
		# text
		# text| >>
		# heading
		set_visual_selection(u'V', 2, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV9gg'))

		# << text
		# x. heading
		# text| >>
		# heading
		set_visual_selection(u'V', 12, 14, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV15gg'))

		set_visual_selection(u'V', 12, 15, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV16gg'))

		set_visual_selection(u'V', 12, 16, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV17gg'))

		# << text
		# text
		# text| >>
		# heading
		# EOF
		set_visual_selection(u'V', 15, 17, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 15ggV20gg'))

		# << text >>
		# heading
		set_visual_selection(u'V', 1, 1, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1ggV5gg'))

		# << heading >>
		# text
		# heading
		set_visual_selection(u'V', 2, 2, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV5gg'))

		# << text >>
		# heading
		set_visual_selection(u'V', 1, 1, cursor_pos=END)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1ggV5gg'))

		# << |text
		# heading
		# text
		# heading
		# text >>
		set_visual_selection(u'V', 1, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV8ggo'))

		# << |heading
		# text
		# heading
		# text >>
		set_visual_selection(u'V', 2, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 6ggV8ggo'))

		# << |heading
		# text >>
		# heading
		set_visual_selection(u'V', 6, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 8ggV9gg'))

		# << |x. heading
		# text >>
		# heading
		set_visual_selection(u'V', 13, 15, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 15ggV15gg'))

		set_visual_selection(u'V', 13, 16, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggV16ggo'))

		set_visual_selection(u'V', 16, 16, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggV17gg'))

		# << |x. heading
		# text >>
		# heading
		# EOF
		set_visual_selection(u'V', 17, 17, cursor_pos=START)
		self.assertNotEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 17ggV20gg'))

		# << |heading
		# text>>
		# text
		# EOF
		set_visual_selection(u'V', 18, 19, cursor_pos=START)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 19ggV20gg'))

		# << heading
		# text|>>
		# text
		# EOF
		set_visual_selection(u'V', 18, 19, cursor_pos=END)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 18ggV20gg'))

		# << heading
		# text|>>
		# EOF
		set_visual_selection(u'V', 18, 20, cursor_pos=END)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 18ggV20gg'))

		# << |heading
		# text>>
		# EOF
		set_visual_selection(u'V', 20, 20, cursor_pos=START)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 20ggV20gg'))

	def test_forward_movement_visual_to_the_end_of_the_file(self):
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
test
""".split(u'\n') ]
		# << |heading
		# text>>
		# EOF
		set_visual_selection(u'V', 15, 15, cursor_pos=START)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 15ggV17gg'))

		set_visual_selection(u'V', 15, 17, cursor_pos=END)
		self.assertEqual(self.navigator.next(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 15ggV17gg'))

	def test_backward_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor position: |

		# << text | >>
		# text
		# heading
		set_visual_selection(u'V', 1, 1, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! gv'))

		set_visual_selection(u'V', 1, 1, cursor_pos=END)
		self.assertEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! gv'))

		# << heading| >>
		# text
		# heading
		set_visual_selection(u'V', 2, 2, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV2ggo'))

		set_visual_selection(u'V', 2, 2, cursor_pos=END)
		self.assertEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV2ggo'))

		# heading
		# text
		# << |text
		# text >>
		set_visual_selection(u'V', 3, 5, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV5ggo'))

		# heading
		# text
		# << text
		# text| >>
		set_visual_selection(u'V', 3, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV3ggo'))

		# heading
		# text
		# << text
		# text| >>
		set_visual_selection(u'V', 8, 9, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 6ggV8ggo'))

		# heading
		# << text
		# x. heading
		# text| >>
		set_visual_selection(u'V', 12, 14, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV12gg'))

		set_visual_selection(u'V', 12, 15, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV12gg'))

		# heading
		# << |text
		# x. heading
		# text >>
		set_visual_selection(u'V', 12, 15, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 10ggV15ggo'))

		# heading
		# << text
		# x. heading| >>
		set_visual_selection(u'V', 12, 13, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV12gg'))

		# heading
		# << text
		# heading
		# text
		# x. heading| >>
		set_visual_selection(u'V', 12, 16, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV15gg'))

		# << text
		# heading
		# text
		# heading| >>
		set_visual_selection(u'V', 15, 17, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 15ggV16gg'))

		# heading
		# << |text
		# text
		# heading
		# text >>
		set_visual_selection(u'V', 4, 8, cursor_pos=START)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV8ggo'))

		# heading
		# << text
		# text
		# heading
		# text| >>
		set_visual_selection(u'V', 4, 8, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 4ggV5gg'))

		# heading
		# << text
		# text
		# heading
		# text| >>
		set_visual_selection(u'V', 4, 5, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV4ggo'))

		# BOF
		# << |heading
		# text
		# heading
		# text >>
		set_visual_selection(u'V', 2, 8, cursor_pos=START)
		self.assertEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV8ggo'))

		# BOF
		# heading
		# << text
		# text| >>
		set_visual_selection(u'V', 3, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV3ggo'))

		# BOF
		# << heading
		# text
		# text| >>
		set_visual_selection(u'V', 2, 4, cursor_pos=END)
		self.assertNotEqual(self.navigator.previous(mode=u'visual'), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV2ggo'))

		# << text
		# heading
		# text
		# x. heading
		# text| >>
		set_visual_selection(u'V', 8, 14, cursor_pos=END)
		self.navigator.previous(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 8ggV12gg'))

	def test_parent_movement_visual(self):
		# selection start: <<
		# selection end:   >>
		# cursor position: |

		# heading
		# << text|
		# text
		# text >>
		set_visual_selection(u'V', 4, 8, cursor_pos=START)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! gv'))

		# heading
		# << text|
		# text
		# text >>
		set_visual_selection(u'V', 6, 8, cursor_pos=START)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV8ggo'))

		# heading
		# << text
		# text
		# text| >>
		set_visual_selection(u'V', 6, 8, cursor_pos=END)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 6ggV5gg'))

		# << |heading
		# text
		# text
		# text >>
		set_visual_selection(u'V', 2, 8, cursor_pos=START)
		self.assertEqual(self.navigator.parent(mode=u'visual'), None)

		# << heading
		# text
		# heading
		# text| >>
		set_visual_selection(u'V', 2, 8, cursor_pos=END)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV5gg'))

		set_visual_selection(u'V', 7, 8, cursor_pos=START)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV8ggo'))

		# heading
		# heading
		# << text
		# text| >>
		set_visual_selection(u'V', 12, 13, cursor_pos=END)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 12ggV12gg'))

		set_visual_selection(u'V', 10, 12, cursor_pos=START)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggV12ggo'))

		# heading
		# << text
		# text
		# heading| >>
		set_visual_selection(u'V', 11, 17, cursor_pos=END)
		self.assertEqual(self.navigator.parent(mode=u'visual'), None)

		# << text
		# heading
		# text
		# x. heading
		# text| >>
		set_visual_selection(u'V', 8, 14, cursor_pos=END)
		self.navigator.parent(mode=u'visual')
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 8ggV12gg'))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(NavigatorTestCase)
