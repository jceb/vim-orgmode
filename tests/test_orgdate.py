# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from datetime import date
from datetime import datetime

from orgmode.liborgmode.orgdate import get_orgdate
from orgmode.liborgmode.orgdate import OrgDate


class OrgDateTestCase(unittest.TestCase):
	u"""
    Tests all the functionality of the OrgDate
	"""

	def setUp(self):
		self.date = date(2011, 8, 29)
		self.year = 2011
		self.month = 8
		self.day = 29

		self.text = '<2011-08-29 Mon>'
		self.textinactive = '[2011-08-29 Mon]'

	def test_OrgDate_ctor(self):
		"""OrdDate should be created."""
		today = date.today()
		od = OrgDate(True, today.year, today.month, today.day)
		self.assertTrue(isinstance(od, OrgDate))
		self.assertTrue(od.active)

		od = OrgDate(False, today.year, today.month, today.day)
		self.assertTrue(isinstance(od, OrgDate))
		self.assertFalse(od.active)

	def test_OrdDate_str(self):
		"""Representation of OrgDates"""
		od = OrgDate(True, self.year, self.month, self.day)
		self.assertEqual(self.text, str(od))

		od = OrgDate(False, self.year, self.month, self.day)
		self.assertEqual(self.textinactive, str(od))


	def test_get_orgdate_parsing(self):
		"""
		get_orgdate should recognice all orgdates in a given text
		"""
		result = get_orgdate(self.text)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertTrue(isinstance(get_orgdate("<2011-08-30 Tue>"), OrgDate))
		self.assertEqual(get_orgdate("<2011-08-30 Tue>").year, 2011)
		self.assertEqual(get_orgdate("<2011-08-30 Tue>").month, 8)
		self.assertEqual(get_orgdate("<2011-08-30 Tue>").day, 30)

		datestr = "This date <2011-08-30 Tue> is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))


	def test_get_orgdate_parsing_with_invalid_input(self):
		self.assertIsNone(get_orgdate("NONSENSE"))
		self.assertIsNone(get_orgdate("No D<2011- Date 08-29 Mon>"))
		self.assertIsNone(get_orgdate("2011-08-r9 Mon]"))
		self.assertIsNone(get_orgdate("<2011-08-29 Mon"))
		self.assertIsNone(get_orgdate("<2011-08-29 Mon]"))
		self.assertIsNone(get_orgdate("2011-08-29 Mon"))
		self.assertIsNone(get_orgdate("2011-08-29"))
		self.assertIsNone(get_orgdate("2011-08-29 mon"))
		self.assertIsNone(get_orgdate("<2011-08-29 mon>"))

		self.assertIsNone(get_orgdate("wrong date embedded <2011-08-29 mon>"))
		self.assertIsNone(get_orgdate("wrong date <2011-08-29 mon>embedded "))


	def test_get_orgdate_parsing_with_invalid_dates(self):
		"""Something like <2011-14-29 Mon> should not be parsed"""
		datestr = "<2011-14-30 Tue>"
		self.assertIsNone(get_orgdate(datestr))

		datestr = "<2012-03-40 Tue>"
		self.assertIsNone(get_orgdate(datestr))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateTestCase)

# vi: noexpandtab
