# -*- coding: utf-8 -*-


import sys
sys.path.append(u'../ftplugin')

import unittest
from orgmode.liborgmode.base import Direction
from orgmode.vimbuffer import VimBuffer
from orgmode.plugins.Todo import Todo

import vim

from orgmode.py3compat.encode_compatibility import *

counter = 0

class TodoTestCase(unittest.TestCase):
	u"""Tests all the functionality of the TODO module."""

	def setUp(self):
		# set content of the buffer
		global counter
		counter += 1
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
				u_encode(u"v:count"): u_encode(u'0')
				}

		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* Heading 1
** Text 1
*** Text 2
* Text 1
** Text 1
   some text that is
   no heading

""".split(u'\n') ]

	# toggle
	def test_toggle_todo_with_no_heading(self):
		# nothing should happen
		vim.current.window.cursor = (1, 0)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[0], u'')
		# and repeat it -> it should not change
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[0], u'')

	def test_todo_toggle_NOTODO(self):
		vim.current.window.cursor = (2, 0)
		vim.current.buffer[1] = u_encode(u'** NOTODO Überschrift 1.1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u_encode(u'** TODO NOTODO Überschrift 1.1'))

	def test_toggle_todo_in_heading_with_no_todo_state_different_levels(self):
		# level 1
		vim.current.window.cursor = (2, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* TODO Heading 1')
		self.assertEqual((2, 0), vim.current.window.cursor)

		# level 2
		vim.current.window.cursor = (3, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[2], u'** TODO Text 1')

		# level 2
		vim.current.window.cursor = (4, 4)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[3], u'*** TODO Text 2')
		self.assertEqual((4, 9), vim.current.window.cursor)

	def test_circle_through_todo_states(self):
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * DONE Heading 1 -->
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * DONE Heading 1
		vim.current.window.cursor = (2, 6)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* TODO Heading 1')
		self.assertEqual((2, 11), vim.current.window.cursor)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* DONE Heading 1')
		self.assertEqual((2, 11), vim.current.window.cursor)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* Heading 1')
		self.assertEqual((2, 6), vim.current.window.cursor)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* TODO Heading 1')
		self.assertEqual((2, 11), vim.current.window.cursor)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* DONE Heading 1')
		self.assertEqual((2, 11), vim.current.window.cursor)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* Heading 1')
		self.assertEqual((2, 6), vim.current.window.cursor)

	def test_circle_through_todo_states_with_more_states(self):
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * STARTED Heading 1 -->
		# * DONE Heading 1 -->
		# * Heading 1 -->
		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'STARTED'), u_encode(u'DONE'),
				u_encode(u'|')]
		vim.current.window.cursor = (2, 0)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* TODO Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* STARTED Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* DONE Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], u'* Heading 1')

	def test_toggle_todo_with_cursor_in_text_not_heading(self):
		# nothing should happen
		vim.current.window.cursor = (7, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[5], u'** TODO Text 1')
		self.assertEqual(vim.current.window.cursor, (7, 0))

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[5], u'** DONE Text 1')
		self.assertEqual(vim.current.window.cursor, (7, 0))

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[5], u'** Text 1')
		self.assertEqual(vim.current.window.cursor, (7, 0))

	# get_states
	def test_get_states_without_seperator(self):
		u"""The last element in the todostates shouold be used as DONE-state when no sperator is given"""
		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo, expected_done = [u'TODO'], [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'INPROGRESS'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO', u'INPROGRESS']
		expected_done = [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'INPROGRESS'),
				u_encode(u'DUMMY'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo  = [u'TODO', u'INPROGRESS', u'DUMMY']
		expected_done = [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

	def test_get_states_with_seperator(self):
		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO']
		expected_done = [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'INPROGRESS'), u_encode(u'|'),
				u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO', u'INPROGRESS']
		expected_done = [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'INPROGRESS'),
				u_encode(u'DUMMY'), u_encode(u'|'),  u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO', u'INPROGRESS', u'DUMMY']
		expected_done = [u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'INPROGRESS'),
				u_encode(u'DUMMY'), u_encode(u'|'), u_encode(u'DELEGATED'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo =[u'TODO', u'INPROGRESS', u'DUMMY']
		expected_done = [u'DELEGATED', u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONEX'),
				u_encode(u'DUMMY'), u_encode(u'DELEGATED'), u_encode(u'DONE')]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO']
		expected_done = [u'DONEX', u'DUMMY', u'DELEGATED', u'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS[u_encode(u'g:org_todo_keywords')] = [[u_encode(u'TODO(t)'), u_encode(u'|'), u_encode(u'DONEX')],
				[u_encode(u'DUMMY'), u_encode(u'DELEGATED'), u_encode(u'DONE')]]
		states_todo, states_done = VimBuffer().get_todo_states()[0]
		expected_todo = [u'TODO']
		expected_done = [u'DONEX']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

	# get_next_state
	def test_get_next_state_with_no_current_state(self):
		states = [((u'TODO', ), (u'DONE', ))]
		current_state = u''
		self.assertEquals(Todo._get_next_state(current_state, states), u'TODO')

		states = [((u'TODO', u'NEXT'), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states), u'TODO')

		states = [((u'NEXT', ), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states), u'NEXT')

	def test_get_next_state_backward_with_no_current_state(self):
		states = [((u'TODO', ), (u'DONE', ))]
		current_state = u''
		self.assertEquals(Todo._get_next_state(current_state, states,
				Direction.BACKWARD), u'DONE')

		states = [((u'TODO', u'NEXT'), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states,
				Direction.BACKWARD), u'DONE')

		states = [((u'NEXT', ), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states,
				Direction.BACKWARD), u'DONE')

	def test_get_next_state_with_invalid_current_state(self):
		states = [((u'TODO', ), (u'DONE', ))]
		current_state = u'STI'
		self.assertEquals(Todo._get_next_state(current_state, states), u'TODO')

		states = [((u'TODO', u'NEXT'), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states), u'TODO')

		states = [((u'NEXT', ), (u'DELEGATED', u'DONE'))]
		self.assertEquals(Todo._get_next_state(current_state, states), u'NEXT')

	def test_get_next_state_backward_with_invalid_current_state(self):
		states = [((u'TODO', ), (u'DONE', ))]
		current_state = u'STI'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'DONE')

		states = [((u'TODO', u'NEXT'), (u'DELEGATED', u'DONE'))]
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'DONE')

		states = [((u'NEXT', ), (u'DELEGATED', u'DONE'))]
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'DONE')

	def test_get_next_state_with_current_state_equals_todo_state(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE'))]
		current_state = u'TODO'
		self.assertEquals(Todo._get_next_state(current_state, states), u'NEXT')

		current_state = u'NEXT'
		self.assertEquals(Todo._get_next_state(current_state, states), u'NOW')

	def test_get_next_state_backward_with_current_state_equals_todo_state(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE'))]
		current_state = u'TODO'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, None)

	def test_get_next_state_backward_misc(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE'))]
		current_state = u'DONE'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'DELEGATED')

		current_state = u'DELEGATED'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'NOW')

		current_state = u'NOW'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'NEXT')

		current_state = u'NEXT'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'TODO')

		current_state = u'TODO'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, None)

		current_state = None
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'DONE')

	def test_get_next_state_with_jump_from_todo_to_done(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE'))]
		current_state = u'NOW'
		self.assertEquals(Todo._get_next_state(current_state, states), u'DELEGATED')

	def test_get_next_state_with_jump_from_done_to_todo(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE'))]
		current_state = u'DONE'
		self.assertEquals(Todo._get_next_state(current_state, states), None)

	def test_get_next_state_in_current_sequence(self):
		states = [((u'TODO', u'NEXT', u'NOW'), (u'DELEGATED', u'DONE')), ((u'QA', ), (u'RELEASED', ))]
		current_state = u'QA'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD)
		self.assertEquals(result, u'RELEASED')

	def test_get_next_state_in_current_sequence_with_access_keys(self):
		states = [((u'TODO(t)', u'NEXT(n)', u'NOW(w)'), (u'DELEGATED(g)', u'DONE(d)')), ((u'QA(q)', ), (u'RELEASED(r)', ))]
		current_state = u'QA'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD)
		self.assertEquals(result, u'RELEASED')

		current_state = u'NEXT'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD)
		self.assertEquals(result, u'NOW')

		current_state = u'TODO'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, None)

		current_state = None
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD)
		self.assertEquals(result, u'RELEASED')

	def test_get_next_keyword_sequence(self):
		states = [((u'TODO(t)', u'NEXT(n)', u'NOW(w)'), (u'DELEGATED(g)', u'DONE(d)')), ((u'QA(q)', ), (u'RELEASED(r)', ))]
		current_state = None
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, u'TODO')

		current_state = None
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD, next_set=True)
		self.assertEquals(result, u'QA')

		current_state = u'TODO'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD, next_set=True)
		self.assertEquals(result, None)

		current_state = u'TODO'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, u'QA')

		current_state = u'NOW'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, u'QA')

		current_state = u'DELEGATED'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, u'QA')

		current_state = u'QA'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD, next_set=True)
		self.assertEquals(result, u'TODO')

		current_state = u'QA'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, None)

		current_state = u'RELEASED'
		result = Todo._get_next_state(current_state, states,
				Direction.FORWARD, next_set=True)
		self.assertEquals(result, None)

		current_state = u'RELEASED'
		result = Todo._get_next_state(current_state, states,
				Direction.BACKWARD, next_set=True)
		self.assertEquals(result, u'TODO')


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TodoTestCase)

# vi: noexpandtab
