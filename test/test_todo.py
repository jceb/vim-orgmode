# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode.plugins.Todo import Todo

class TodoTestCase(unittest.TestCase):
	"""Tests all the functionality of the TODO module."""

	def setUp(self):
		# register todo plugin
		# why does it work without this?
		#if not 'Todo' in ORGMODE.plugins:
			#ORGMODE.register_plugin('Todo')

		# set content of the buffer
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				'exists("b:org_todo_keywords")': 0,
				# global values for org_todo_keywords
				'exists("g:org_todo_keywords")': 1,
				'g:org_todo_keywords': ['TODO', 'DONE', '|'],
				}

		vim.current.buffer = """
* Heading 1
** Text 1
*** Text 2
* Text 1
** Text 1
""".split('\n')

	def test_toggle_todo_with_no_heading(self):
		# nothing should happen
		vim.current.window.cursor = (1, 0)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[0], '')
		# and repeat it -> it should not change
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[0], '')

	def test_toggle_todo_in_heading_with_no_todo_state_different_levels(self):
		# level 1
		vim.current.window.cursor = (2, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* TODO Heading 1')

		# level 2
		vim.current.window.cursor = (3, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[2], '** TODO Text 1')

		# level 2
		vim.current.window.cursor = (4, 0)
		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[3], '*** TODO Text 2')

	def test_circle_through_todo_states(self):
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * DONE Heading 1 -->
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * DONE Heading 1
		vim.current.window.cursor = (2, 0)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* TODO Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* DONE Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* TODO Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* DONE Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* Heading 1')

	def test_circle_through_todo_states_with_more_states(self):
		# * Heading 1 -->
		# * TODO Heading 1 -->
		# * STARTED Heading 1 -->
		# * DONE Heading 1 -->
		# * Heading 1 -->
		vim.EVALRESULTS['g:org_todo_keywords'] = ['TODO', 'STARTED', 'DONE',
				'|']
		vim.current.window.cursor = (2, 0)

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* TODO Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* STARTED Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* DONE Heading 1')

		Todo.toggle_todo_state()
		self.assertEqual(vim.current.buffer[1], '* Heading 1')

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TodoTestCase)

# vi: noexpandtab
