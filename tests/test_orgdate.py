# -*- coding: utf-8 -*-


import sys
import unittest
from datetime import date
from datetime import datetime

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import OrgDate
from orgmode.liborgmode.orgdate import OrgDateTime


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
		self.assertEqual(self.text, str(od))

	def test_OrdDate_str_inactive(self):
		od = OrgDate(False, self.year, self.month, self.day)
		self.assertEqual(self.textinactive, str(od))


class OrgDateTimeTestCase(unittest.TestCase):
	u"""
	Tests all the functionality of the OrgDateTime
	"""

	def test_OrgDateTime_ctor_active(self):
		u"""OrdDateTime should be created."""
		today = datetime.today()
		odt = OrgDateTime(True, today.year, today.month, today.day, today.hour,
				today.minute)
		self.assertTrue(isinstance(odt, OrgDateTime))
		self.assertTrue(odt.active)

	def test_OrgDateTime_ctor_inactive(self):
		u"""OrdDateTime should be created."""
		today = datetime.today()
		odt = OrgDateTime(False, today.year, today.month, today.day, today.hour,
				today.minute)
		self.assertTrue(isinstance(odt, OrgDateTime))
		self.assertFalse(odt.active)

	def test_OrdDateTime_str_active(self):
		u"""Representation of OrgDateTime"""
		t = 2011, 9, 8, 10, 20
		odt = OrgDateTime(False, t[0], t[1], t[2], t[3], t[4])
		self.assertEqual("[2011-09-08 Thu 10:20]", str(odt))

	def test_OrdDateTime_str_inactive(self):
		u"""Representation of OrgDateTime"""
		t = 2011, 9, 8, 10, 20
		odt = OrgDateTime(True, t[0], t[1], t[2], t[3], t[4])
		self.assertEqual("<2011-09-08 Thu 10:20>", str(odt))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateTestCase)

# vi: noexpandtab
