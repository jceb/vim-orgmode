# -*- coding: utf-8 -*-


import sys
import unittest
from datetime import date

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import OrgDate

from orgmode.py3compat.unicode_compatibility import *

class OrgDateTestCase(unittest.TestCase):
	u"""
	Tests all the functionality of the OrgDate
	"""

	def setUp(self):
		self.date = date(2011, 8, 29)
		self.year = 2011
		self.month = 8
		self.day = 29
		self.text = u'<2011-08-29 Mon>'
		self.textinactive = u'[2011-08-29 Mon]'

	def test_OrgDate_ctor_active(self):
		u"""OrdDate should be created."""
		today = date.today()
		od = OrgDate(True, today.year, today.month, today.day)
		self.assertTrue(isinstance(od, OrgDate))
		self.assertTrue(od.active)

	def test_OrgDate_ctor_inactive(self):
		u"""OrdDate should be created."""
		today = date.today()
		od = OrgDate(False, today.year, today.month, today.day)
		self.assertTrue(isinstance(od, OrgDate))
		self.assertFalse(od.active)

	def test_OrdDate_str_active(self):
		u"""Representation of OrgDates"""
		od = OrgDate(True, self.year, self.month, self.day)
		self.assertEqual(self.text, unicode(od))

	def test_OrdDate_str_inactive(self):
		od = OrgDate(False, self.year, self.month, self.day)
		self.assertEqual(self.textinactive, unicode(od))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateTestCase)

# vi: noexpandtab
