# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from orgmode.liborgmode.headings import Heading
from orgmode.liborgmode.orgdate import OrgDate


class TestHeadingRecognizeDatesInHeading(unittest.TestCase):

	def setUp(self):
		self.allowed_todo_states = ["TODO"]

	def test_heading_parsing_no_date(self):
		"""""
		'text' doesn't contain any valid date.
		"""
		text = ["* TODO This is a test :hallo:"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(None, h.active_date)

		text = ["* TODO This is a test <2011-08-25>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(None, h.active_date)

		text = ["* TODO This is a test <2011-08-25 Wednesday>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(None, h.active_date)

		text = ["* TODO This is a test <20110825>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(None, h.active_date)

	def test_heading_parsing_with_date(self):
		"""""
		'text' does contain valid dates.
		"""
		text = ["* TODO This is a test <2011-08-24 Wed> :hallo:"]
		odate = OrgDate(True, 2011, 8, 24)
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(odate, h.active_date)

		#TODO: orgdatetime is not implemented yet
		#text = ["* TODO This is a test <2011-08-25 Thu 10:10> :hallo:"]
		#odate = OrgDate(True, 2011, 8, 25, 10, 10)
		#h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		#self.assertEqual(odate, h.active_date)

	def test_heading_parsing_with_date_and_body(self):
		"""""
		'text' contains valid dates (in the body).
		"""
		#TODO: orgdatetime is not implemented yet
		#text = ["* TODO This is a test <2011-08-25 Thu 10:10> :hallo:",
				#"some body text",
				#"some body text"]
		#h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		#self.assertEqual("2011-08-25-10-10", h.active_date)

		#text = ["* TODO This is a test  :hallo:",
				#"some body text",
				#"some body text<2011-08-25 Thu 10:10>"]
		#h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		#self.assertEqual("2011-08-25-10-10", h.active_date)

		text = ["* TODO This is a test  :hallo:",
				"some body text <2011-08-24 Wed>",
				"some body text<2011-08-25 Thu 10:10>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		odate = OrgDate(True, 2011, 8, 24)
		self.assertEqual(odate, h.active_date)

	def test_sorting_of_headings(self):
		"""Headings should be sortable."""
		# setup some fixtures
		tmp = ["* This heading is earlier  <2011-08-24 Wed>"]
		h1 = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)
		tmp = ["* This heading is later <2011-08-25 Thu>"]
		h2 = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)
		tmp = ["* This heading has no date and should be later than the rest"]
		h_no_date = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)

		self.assertLess(h1, h2)
		self.assertLess(h1, h_no_date)
		self.assertLess(h2, h_no_date)

		self.assertLessEqual(h1, h2)
		self.assertLessEqual(h1, h_no_date)
		self.assertLessEqual(h2, h_no_date)

		self.assertGreater(h2, h1)
		self.assertGreater(h_no_date, h1)
		self.assertGreater(h_no_date, h2)

		self.assertGreaterEqual(h2, h1)
		self.assertGreaterEqual(h_no_date, h1)
		self.assertGreaterEqual(h_no_date, h2)

		# test sorting
		self.assertEqual([h1, h2], sorted([h2, h1]))
		self.assertEqual([h1, h2], sorted([h1, h2]))
		self.assertEqual([h1, h_no_date], sorted([h1, h_no_date]))
		self.assertEqual([h1, h_no_date], sorted([h_no_date, h1]))
		self.assertEqual([h1, h2, h_no_date], sorted([h2, h_no_date, h1]))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(
			TestHeadingRecognizeDatesInHeading)

# vim: set noexpandtab:
