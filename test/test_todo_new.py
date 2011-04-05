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

# vim: set noexpandtab
