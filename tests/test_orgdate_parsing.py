# -*- coding: utf-8 -*-


import sys
import unittest

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import get_orgdate, OrgDate


class OrgDateParsingTestCase(unittest.TestCase):
	u"""
	Tests the functionality of the parsing function of OrgDate.

	Mostly function get_orgdate().
	"""

	def setUp(self):
		self.text = '<2011-08-29 Mon>'
		self.textinactive = '[2011-08-29 Mon]'

	def test_get_orgdate_parsing_active(self):
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
		self.assertTrue(get_orgdate("<2011-08-30 Tue>").active)

		datestr = "This date <2011-08-30 Tue> is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))

	def test_get_orgdate_parsing_inactive(self):
		"""
		get_orgdate should recognice all inactive orgdates in a given text
		"""
		result = get_orgdate(self.textinactive)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertTrue(isinstance(get_orgdate("[2011-08-30 Tue]"), OrgDate))
		self.assertEqual(get_orgdate("[2011-08-30 Tue]").year, 2011)
		self.assertEqual(get_orgdate("[2011-08-30 Tue]").month, 8)
		self.assertEqual(get_orgdate("[2011-08-30 Tue]").day, 30)
		self.assertFalse(get_orgdate("[2011-08-30 Tue]").active)

		datestr = "This date [2011-08-30 Tue] is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))

	def test_get_orgdate_parsing_with_list_of_texts(self):
		"""
		get_orgdate should return the first date in the list.
		"""
		datelist = ["<2011-08-29 Mon>"]
		result = get_orgdate(datelist)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = ["<2011-08-29 Mon>",
				"<2012-03-30 Fri>"]
		result = get_orgdate(datelist)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = ["some <2011-08-29 Mon>text",
				"<2012-03-30 Fri> is here"]
		result = get_orgdate(datelist)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = ["here is no date",
				"some <2011-08-29 Mon>text",
				"<2012-03-30 Fri> is here"]
		result = get_orgdate(datelist)
		self.assertIsNotNone(result)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

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
		"""
		Something like <2011-14-29 Mon> (invalid dates, they don't exist)
		should not be parsed
		"""
		datestr = "<2011-14-30 Tue>"
		self.assertIsNone(get_orgdate(datestr))

		datestr = "<2012-03-40 Tue>"
		self.assertIsNone(get_orgdate(datestr))


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateParsingTestCase)

# vim: noexpandtab
