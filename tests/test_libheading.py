# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from orgmode.liborgmode.headings import Heading
from orgmode.liborgmode.orgdate import OrgDate
from orgmode.liborgmode.orgdate import OrgDateTime


class TestHeadingRecognizeDatesInHeading(unittest.TestCase):

	def setUp(self):
		self.allowed_todo_states = ["TODO"]

		tmp = ["* This heading is earlier  <2011-08-24 Wed>"]
		self.h1 = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)

		tmp = ["* This heading is later <2011-08-25 Thu>"]
		self.h2 = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)

		tmp = ["* This heading is later <2011-08-25 Thu 10:20>"]
		self.h2_datetime = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)

		tmp = ["* This heading is later <2011-08-26 Fri 10:20>"]
		self.h3 = Heading.parse_heading_from_data(tmp, self.allowed_todo_states)

		tmp = ["* This heading has no date and should be later than the rest"]
		self.h_no_date = Heading.parse_heading_from_data(tmp,
				self.allowed_todo_states)

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
		# orgdate
		text = ["* TODO This is a test <2011-08-24 Wed> :hallo:"]
		odate = OrgDate(True, 2011, 8, 24)
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(odate, h.active_date)

		# orgdatetime
		text = ["* TODO This is a test <2011-08-25 Thu 10:10> :hallo:"]
		odate = OrgDateTime(True, 2011, 8, 25, 10, 10)
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertEqual(odate, h.active_date)

	def test_heading_parsing_with_date_and_body(self):
		"""""
		'text' contains valid dates (in the body).
		"""
		# orgdatetime
		text = ["* TODO This is a test <2011-08-25 Thu 10:10> :hallo:",
				"some body text",
				"some body text"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertTrue(isinstance(h.active_date, OrgDateTime))
		self.assertEqual("<2011-08-25 Thu 10:10>", str(h.active_date))

		text = ["* TODO This is a test  :hallo:",
				"some body text",
				"some body text<2011-08-25 Thu 10:10>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		self.assertTrue(isinstance(h.active_date, OrgDateTime))
		self.assertEqual("<2011-08-25 Thu 10:10>", str(h.active_date))

		text = ["* TODO This is a test  :hallo:",
				"some body text <2011-08-24 Wed>",
				"some body text<2011-08-25 Thu 10:10>"]
		h = Heading.parse_heading_from_data(text, self.allowed_todo_states)
		odate = OrgDate(True, 2011, 8, 24)
		self.assertEqual(odate, h.active_date)

	def test_less_than_for_dates_in_heading(self):
		self.assertTrue(self.h1 < self.h2)
		self.assertTrue(self.h1 < self.h3)
		self.assertTrue(self.h1 < self.h_no_date)
		self.assertTrue(self.h2 < self.h_no_date)
		self.assertTrue(self.h2 < self.h3)
		self.assertTrue(self.h3 < self.h_no_date)

		self.assertFalse(self.h2 < self.h1)
		self.assertFalse(self.h3 < self.h2)

	def test_less_equal_for_dates_in_heading(self):
		self.assertTrue(self.h1 <= self.h2)
		self.assertTrue(self.h1 <= self.h_no_date)
		self.assertTrue(self.h2 <= self.h_no_date)
		self.assertTrue(self.h2 <= self.h2_datetime)
		self.assertTrue(self.h2 <= self.h3)

	def test_greate_than_for_dates_in_heading(self):
		self.assertTrue(self.h2 > self.h1)
		self.assertTrue(self.h_no_date > self.h1)
		self.assertTrue(self.h_no_date > self.h2)

		self.assertFalse(self.h2 > self.h2_datetime)

	def test_greate_equal_for_dates_in_heading(self):
		self.assertTrue(self.h2 >= self.h1)
		self.assertTrue(self.h_no_date >= self.h1)
		self.assertTrue(self.h_no_date >= self.h2)
		self.assertTrue(self.h2 >= self.h2_datetime)

	def test_sorting_of_headings(self):
		"""Headings should be sortable."""
		self.assertEqual([self.h1, self.h2], sorted([self.h2, self.h1]))

		self.assertEqual([self.h1, self.h2_datetime],
				sorted([self.h2_datetime, self.h1]))

		self.assertEqual([self.h2_datetime, self.h2],
				sorted([self.h2_datetime, self.h2]))

		self.assertEqual([self.h1, self.h2], sorted([self.h1, self.h2]))

		self.assertEqual([self.h1, self.h_no_date],
				sorted([self.h1, self.h_no_date]))

		self.assertEqual([self.h1, self.h_no_date],
				sorted([self.h_no_date, self.h1]))

		self.assertEqual([self.h1, self.h2, self.h_no_date],
				sorted([self.h2, self.h_no_date, self.h1]))

		self.assertEqual(
				[self.h1, self.h2_datetime, self.h2, self.h3, self.h_no_date],
				sorted([self.h2_datetime, self.h3, self.h2, self.h_no_date, self.h1]))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(
			TestHeadingRecognizeDatesInHeading)

# vim: set noexpandtab:
