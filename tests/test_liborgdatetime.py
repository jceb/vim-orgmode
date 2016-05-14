# -*- coding: utf-8 -*-

import sys
import unittest
from datetime import datetime

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import OrgDateTime

from orgmode.py3compat.unicode_compatibility import *

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
		self.assertEqual(u"[2011-09-08 Thu 10:20]", unicode(odt))

	def test_OrdDateTime_str_inactive(self):
		u"""Representation of OrgDateTime"""
		t = 2011, 9, 8, 10, 20
		odt = OrgDateTime(True, t[0], t[1], t[2], t[3], t[4])
		self.assertEqual(u"<2011-09-08 Thu 10:20>", unicode(odt))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateTimeTestCase)


# vim: noexpandtab
