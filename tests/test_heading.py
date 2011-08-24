# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from orgmode.liborgmode.liborgmode import Heading


class TestHeading(unittest.TestCase):

	def setUp(self):
		pass

	def test_heading_parsing(self):
		allowed_todo_states = ["TODO"]

		text = ["* TODO This is a test :hallo:"]
		heading = Heading.parse_heading_from_data(text, allowed_todo_states)
		self.assertEqual(None, heading.active_date)

		text = ["* TODO This is a test <2011-08-24 Wed> :hallo:"]
		heading = Heading.parse_heading_from_data(text, allowed_todo_states)
		self.assertEqual("2011-08-24", heading.active_date)


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(TestHeading)

# vim: set noexpandtab:
