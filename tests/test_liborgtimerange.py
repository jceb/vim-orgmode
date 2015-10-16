# -*- coding: utf-8 -*-


import sys
import unittest
from datetime import date
from datetime import datetime

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import OrgTimeRange


class OrgTimeRangeTestCase(unittest.TestCase):

	def setUp(self):
		self.date = date(2011, 8, 29)
		self.year = 2011
		self.month = 8
		self.day = 29
		self.text = '<2011-08-29 Mon>'
		self.textinactive = '[2011-08-29 Mon]'

	def test_OrgTimeRange_ctor_active(self):
		u"""
		timerange should be created.
		"""
		start = date(2011, 9 , 12)
		end = date(2011, 9 , 13)
		timerange = OrgTimeRange(True, start, end)
		self.assertTrue(isinstance(timerange, OrgTimeRange))
		self.assertTrue(timerange.active)

	def test_OrgTimeRange_ctor_inactive(self):
		u"""
		timerange should be created.
		"""
		start = date(2011, 9 , 12)
		end = date(2011, 9 , 13)
		timerange = OrgTimeRange(False, start, end)
		self.assertTrue(isinstance(timerange, OrgTimeRange))
		self.assertFalse(timerange.active)

	def test_OrdDate_str_active(self):
		u"""Representation of OrgDates"""
		start = date(2011, 9 , 12)
		end = date(2011, 9 , 13)
		timerange = OrgTimeRange(True, start, end)
		expected = "<2011-09-12 Mon>--<2011-09-13 Tue>"
		self.assertEqual(str(timerange), expected)

		start = datetime(2011, 9 , 12, 20, 00)
		end = datetime(2011, 9 , 13, 21, 59)
		timerange = OrgTimeRange(True, start, end)
		expected = "<2011-09-12 Mon 20:00>--<2011-09-13 Tue 21:59>"
		self.assertEqual(str(timerange), expected)

		start = datetime(2011, 9 , 12, 20, 00)
		end = datetime(2011, 9 , 12, 21, 00)
		timerange = OrgTimeRange(True, start, end)
		expected = "<2011-09-12 Mon 20:00-21:00>"
		self.assertEqual(str(timerange), expected)

	def test_OrdDate_str_inactive(self):
		u"""Representation of OrgDates"""
		start = date(2011, 9 , 12)
		end = date(2011, 9 , 13)
		timerange = OrgTimeRange(False, start, end)
		expected = "[2011-09-12 Mon]--[2011-09-13 Tue]"
		self.assertEqual(str(timerange), expected)

		start = datetime(2011, 9 , 12, 20, 00)
		end = datetime(2011, 9 , 13, 21, 59)
		timerange = OrgTimeRange(False, start, end)
		expected = "[2011-09-12 Mon 20:00]--[2011-09-13 Tue 21:59]"
		self.assertEqual(str(timerange), expected)

		start = datetime(2011, 9 , 12, 20, 00)
		end = datetime(2011, 9 , 12, 21, 00)
		timerange = OrgTimeRange(False, start, end)
		expected = "[2011-09-12 Mon 20:00-21:00]"
		self.assertEqual(str(timerange), expected)

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgTimeRangeTestCase)

# vim: noexpandtab
