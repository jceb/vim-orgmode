# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

from datetime import date

from orgmode.plugins.Date import Date


class DateTestCase(unittest.TestCase):
	"""Tests all the functionality of the Date plugin."""

	def setUp(self):
		self.d = date(2011, 5, 22)

	def test_modify_time_with_None(self):
		# no modification should happen
		res = Date._modify_time(self.d, None)
		self.assertEquals(self.d, res)

	def test_modify_time_with_given_relative_days(self):
		# modifier and expected result
		test_data = [('+0d', self.d),
				('+1d', date(2011, 5, 23)),
				('+2d', date(2011, 5, 24)),
				('+7d', date(2011, 5, 29)),
				('+9d', date(2011, 5, 31)),
				('+10d', date(2011, 6, 1)),
				('7d', self.d)  # wrong format: plus is missing
				]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_weeks(self):
		# modifier and expected result
		test_data = [('+1w', date(2011, 5, 29)),
				('+2w', date(2011, 6, 5)),
				('+3w', date(2011, 6, 12)),
				('+3w', date(2011, 6, 12)),
				('+0w', self.d),
				('3w', self.d),  # wrong format
				('+w', self.d)]  # wrong format

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_months(self):
		test_data = [('+0m', self.d),
				('+1m', date(2011, 6, 22)),
				('+2m', date(2011, 7, 22))]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_years(self):
		test_data = [('+1y', date(2012, 5, 22)),
				('+10y', date(2021, 5, 22)),
				('+0y', self.d)]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_real_dates(self):
		res = Date._modify_time(self.d, '2011-01-12')
		expected = date(2011, 1, 12)
		self.assertEquals(expected, res)

		res = Date._modify_time(self.d, '2015-03-12')
		expected = date(2015, 3, 12)
		self.assertEquals(expected, res)

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(DateTestCase)

# vi: noexpandtab
