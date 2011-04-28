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
				('7d', self.d)]  # wrong format: plus is missing

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

	def test_modify_time_with_given_weekday(self):
		# use custom day instead of self.d to ease testing
		cust_day = date(2011, 5, 25)  # it's a Wednesday
		#print cust_day.weekday()  # 2
		test_data = [('Thu', date(2011, 5, 26)),
				('thu', date(2011, 5, 26)),
				('tHU', date(2011, 5, 26)),
				('THU', date(2011, 5, 26)),
				('Fri', date(2011, 5, 27)),
				('sat', date(2011, 5, 28)),
				('sun', date(2011, 5, 29)),
				('mon', date(2011, 5, 30)),
				('tue', date(2011, 5, 31)),
				('wed', date(2011, 6, 1))]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(cust_day, modifier))

	def test_modify_time_with_abbreviated_dates(self):
		# use ``d`` instead of ``self.d`` in order to use the same date as in
		# the orgmode documentation:
		# http://orgmode.org/manual/The-date_002ftime-prompt.html#The-date_002ftime-prompt
		d = date(2006, 6, 13)
		test_data = [
				('3-2-5', date(2003, 2, 05)),
				('12-2-28', date(2012, 2, 28)),
				('2/5/3', date(2003, 02, 05)),
				('14', date(2006, 06, 14)),
				('12', date(2006, 07, 12)),
				#('2/5', date(2007, 02, 05))
#Fri            nearest Friday (default date or later)
     #sep 15         2006-09-15
     #feb 15         2007-02-15
     #sep 12 9       2009-09-12
     #12:45          2006-06-13 12:45
     #22 sept 0:34   2006-09-22 0:34
     #w4             ISO week for of the current year 2006
     #2012 w4 fri    Friday of ISO week 4 in 2012
     #2012-w04-5     Same as above
				]

		for modifier, expected in test_data:
			self.assertEquals(expected, Date._modify_time(d, modifier))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(DateTestCase)

# vi: noexpandtab
