# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode.plugins.Todo import Todo

class TodoNewTestCase(unittest.TestCase):

	def setUp(self):
		# set content of the buffer
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				'exists("b:org_todo_keywords")': 0,
				# global values for org_todo_keywords
				'exists("g:org_todo_keywords")': 1,
				'g:org_todo_keywords': ['TODO', 'DONE']
				}

		vim.current.buffer = """
		""".split('\n')

	def test_get_states_without_seperator(self):
		"""The last element in the todostates shouold be used as DONE-state when no sperator is given"""
		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo, expected_done = ['TODO'], ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'INPROGRESS', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo = ['TODO', 'INPROGRESS']
		expected_done = ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'INPROGRESS',
				'DUMMY', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo  = ['TODO', 'INPROGRESS', 'DUMMY']
		expected_done = ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

	def test_get_states_with_seperator(self):
		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', '|', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo = ['TODO']
		expected_done = ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'INPROGRESS', '|',
				'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo = ['TODO', 'INPROGRESS']
		expected_done = ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'INPROGRESS',
				'DUMMY', '|',  'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo = ['TODO', 'INPROGRESS', 'DUMMY']
		expected_done = ['DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'INPROGRESS',
				'DUMMY', '|', 'DELEGATED', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo =['TODO', 'INPROGRESS', 'DUMMY']
		expected_done = ['DELEGATED', 'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', '|', 'DONEX',
				'DUMMY', 'DELEGATED', 'DONE']
		states_todo, states_done = Todo._get_states()
		expected_todo = ['TODO']
		expected_done = ['DONEX', 'DUMMY', 'DELEGATED', 'DONE']
		self.assertEqual(states_todo, expected_todo)
		self.assertEqual(states_done, expected_done)

	def test_get_next_state_with_no_current_state(self):
		states = ['TODO', 'DONE']
		current_state = ''
		self.assertEquals(Todo._get_next_state(current_state, states), 'TODO')

		states = ['TODO', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states), 'TODO')
		states = ['NEXT', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states), 'NEXT')

	def test_get_next_state_backward_with_no_current_state(self):
		states = ['TODO', 'DONE']
		current_state = ''
		self.assertEquals(Todo._get_next_state(current_state, states, False), 'DONE')

		states = ['TODO', 'NEXT', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states, False), 'DONE')

		states = ['NEXT', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states, False), 'DONE')

	def test_get_next_state_with_invalid_current_state(self):
		states = ['TODO', 'DONE']
		current_state = 'STI'
		self.assertEquals(Todo._get_next_state(current_state, states), 'TODO')

		states = ['TODO', 'NEXT', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states), 'TODO')
		states = ['NEXT', 'DELEGATED', 'DONE']
		self.assertEquals(Todo._get_next_state(current_state, states), 'NEXT')

	def test_get_next_state_backward_with_invalid_current_state(self):
		states = ['TODO', 'DONE']
		current_state = 'STI'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'DONE')

		states = ['TODO', 'NEXT', 'DELEGATED', 'DONE']
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'DONE')

		states = ['NEXT', 'DELEGATED', 'DONE']
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'DONE')

	def test_get_next_state_with_current_state_equals_todo_state(self):
		states = ['TODO', 'NEXT', 'NOW', 'DELEGATED', 'DONE']
		current_state = 'TODO'
		self.assertEquals(Todo._get_next_state(current_state, states), 'NEXT')

		current_state = 'NEXT'
		self.assertEquals(Todo._get_next_state(current_state, states), 'NOW')

	def test_get_next_state_backward_with_current_state_equals_todo_state(self):
		states = ['TODO', 'NEXT', 'NOW', 'DELEGATED', 'DONE']
		current_state = 'TODO'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, None)

	def test_get_next_state_backward_misc(self):
		states = ['TODO', 'NEXT', 'NOW', 'DELEGATED', 'DONE']
		current_state = 'DONE'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'DELEGATED')

		current_state = 'DELEGATED'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'NOW')

		current_state = 'NOW'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'NEXT')

		current_state = 'NEXT'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'TODO')

		current_state = 'TODO'
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, None)

		current_state = None
		result = Todo._get_next_state(current_state, states, False)
		self.assertEquals(result, 'DONE')

	def test_get_next_state_with_jump_from_todo_to_done(self):
		states = ['TODO', 'NEXT', 'NOW', 'DELEGATED', 'DONE']
		current_state = 'NOW'
		self.assertEquals(Todo._get_next_state(current_state, states), 'DELEGATED')

	def test_get_next_state_with_jump_from_done_to_todo(self):
		states = ['TODO', 'NEXT', 'NOW', 'DELEGATED', 'DONE']
		current_state = 'DONE'
		self.assertEquals(Todo._get_next_state(current_state, states), None)
# vim: set noexpandtab:
