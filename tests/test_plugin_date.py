# -*- coding: utf-8 -*-

from __future__ import print_function

import unittest
import sys
sys.path.append(u'../ftplugin')

from datetime import date
from datetime import datetime

from orgmode.plugins.Date import Date


class DateTestCase(unittest.TestCase):
	u"""Tests all the functionality of the Date plugin.

	Also see:
	http://orgmode.org/manual/The-date_002ftime-prompt.html#The-date_002ftime-prompt
	"""

	def setUp(self):
		self.d = date(2011, 5, 22)

	def test_modify_time_with_None(self):
		# no modification should happen
		res = Date._modify_time(self.d, None)
		self.assertEquals(self.d, res)

	def test_modify_time_with_dot(self):
		# no modification should happen
		res = Date._modify_time(self.d, u'.')
		self.assertEquals(self.d, res)

	def test_modify_time_with_given_relative_days(self):
		# modifier and expected result
		test_data = [(u'+0d', self.d),
				(u'+1d', date(2011, 5, 23)),
				(u'+2d', date(2011, 5, 24)),
				(u'+7d', date(2011, 5, 29)),
				(u'+9d', date(2011, 5, 31)),
				(u'+10d', date(2011, 6, 1)),
				(u'7d', self.d)]  # wrong format: plus is missing

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_days_without_d(self):
		# modifier and expected result
		test_data = [(u'+0', self.d),
				(u'+1', date(2011, 5, 23)),
				(u'+2', date(2011, 5, 24)),
				(u'+7', date(2011, 5, 29)),
				(u'+9', date(2011, 5, 31)),
				(u'+10', date(2011, 6, 1))]

		for modifier, expected in test_data:
			result = Date._modify_time(self.d, modifier)
			self.assertEquals(expected, result)

	def test_modify_time_with_given_relative_weeks(self):
		# modifier and expected result
		test_data = [(u'+1w', date(2011, 5, 29)),
				(u'+2w', date(2011, 6, 5)),
				(u'+3w', date(2011, 6, 12)),
				(u'+3w', date(2011, 6, 12)),
				(u'+0w', self.d),
				(u'3w', self.d),  # wrong format
				(u'+w', self.d)]  # wrong format

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_months(self):
		test_data = [(u'+0m', self.d),
				(u'+1m', date(2011, 6, 22)),
				(u'+2m', date(2011, 7, 22))]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))

	def test_modify_time_with_given_relative_years(self):
		test_data = [(u'+1y', date(2012, 5, 22)),
				(u'+10y', date(2021, 5, 22)),
				(u'+0y', self.d)]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(self.d, modifier))


	def test_modify_time_with_given_weekday(self):
		# use custom day instead of self.d to ease testing
		cust_day = date(2011, 5, 25)  # it's a Wednesday
		#print(cust_day.weekday())  # 2
		test_data = [(u'Thu', date(2011, 5, 26)),
				(u'thu', date(2011, 5, 26)),
				(u'tHU', date(2011, 5, 26)),
				(u'THU', date(2011, 5, 26)),
				(u'Fri', date(2011, 5, 27)),
				(u'sat', date(2011, 5, 28)),
				(u'sun', date(2011, 5, 29)),
				(u'mon', date(2011, 5, 30)),
				(u'tue', date(2011, 5, 31)),
				(u'wed', date(2011, 6, 1))]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(cust_day, modifier))

	def test_modify_time_with_month_and_day(self):
		cust_date = date(2006, 6, 13)
		test_data = [(u'sep 15', date(2006, 9, 15)),
				(u'Sep 15', date(2006, 9, 15)),
				(u'SEP 15', date(2006, 9, 15)),
				(u'feb 15', date(2007, 2, 15)),
				(u'jan 1', date(2007, 1, 1)),
				(u'7/5', date(2006, 7, 5)),
				(u'2/5', date(2007, 2, 5)),]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(cust_date, modifier))

	def test_modify_time_with_time(self):
		cust_date = date(2006, 6, 13)
		test_data = [(u'12:45', datetime(2006, 6, 13, 12, 45)),
				(u'1:45', datetime(2006, 6, 13, 1, 45)),
				(u'1:05', datetime(2006, 6, 13, 1, 5)),]

		for modifier, expected in test_data:
			res = Date._modify_time(cust_date, modifier)
			self.assertTrue(isinstance(res, datetime))
			self.assertEquals(expected, res)

	def test_modify_time_with_full_dates(self):
		result = Date._modify_time(self.d, u'2011-01-12')
		expected = date(2011, 1, 12)
		self.assertEquals(expected, result)

		reults = Date._modify_time(self.d, u'2015-03-12')
		expected = date(2015, 3, 12)
		self.assertEquals(expected, reults)

		cust_date = date(2006, 6, 13)
		test_data = [(u'3-2-5', date(2003, 2, 5)),
				(u'12-2-28', date(2012, 2, 28)),
				(u'2/5/3', date(2003, 2, 5)),
				(u'sep 12 9', date(2009, 9, 12)),
				(u'jan 2 99', date(2099, 1, 2)),]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(cust_date, modifier))

	def test_modify_time_with_only_days(self):
		cust_date = date(2006, 6, 13)
		test_data = [(u'14', date(2006, 6, 14)),
				(u'12', date(2006, 7, 12)),
				(u'1', date(2006, 7, 1)),
				(u'29', date(2006, 6, 29)),]
		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(cust_date, modifier))

	def test_modify_time_with_day_and_time(self):
		cust_date = date(2006, 6, 13)
		test_data = [(u'+1 10:20', datetime(2006, 6, 14, 10, 20)),
				(u'+1w 10:20', datetime(2006, 6, 20, 10, 20)),
				(u'+2 10:30', datetime(2006, 6, 15, 10, 30)),
				(u'+2d 10:30', datetime(2006, 6, 15, 10, 30))]
		for modifier, expected in test_data:
			result = Date._modify_time(cust_date, modifier)
			self.assertEquals(expected, result)

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(DateTestCase)

# vi: noexpandtab
