# -*- coding: utf-8 -*-


import sys
import unittest

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import get_orgdate
from orgmode.liborgmode.orgdate import OrgDate
from orgmode.liborgmode.orgdate import OrgDateTime
from orgmode.liborgmode.orgdate import OrgTimeRange

from orgmode.py3compat.unicode_compatibility import *

class OrgDateParsingTestCase(unittest.TestCase):
	u"""
	Tests the functionality of the parsing function of OrgDate.

	Mostly function get_orgdate().
	"""

	def setUp(self):
		self.text = u'<2011-08-29 Mon>'
		self.textinactive = u'[2011-08-29 Mon]'

	def test_get_orgdate_parsing_active(self):
		u"""
		get_orgdate should recognize all orgdates in a given text
		"""
		result = get_orgdate(self.text)
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertTrue(isinstance(get_orgdate(u"<2011-08-30 Tue>"), OrgDate))
		self.assertEqual(get_orgdate(u"<2011-08-30 Tue>").year, 2011)
		self.assertEqual(get_orgdate(u"<2011-08-30 Tue>").month, 8)
		self.assertEqual(get_orgdate(u"<2011-08-30 Tue>").day, 30)
		self.assertTrue(get_orgdate(u"<2011-08-30 Tue>").active)

		datestr = u"This date <2011-08-30 Tue> is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))


	def test_get_orgdatetime_parsing_active(self):
		u"""
		get_orgdate should recognize all orgdatetimes in a given text
		"""
		result = get_orgdate(u"<2011-09-12 Mon 10:20>")
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDateTime))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 9)
		self.assertEqual(result.day, 12)
		self.assertEqual(result.hour, 10)
		self.assertEqual(result.minute, 20)
		self.assertTrue(result.active)

		result = get_orgdate(u"some datetime <2011-09-12 Mon 10:20> stuff")
		self.assertTrue(isinstance(result, OrgDateTime))


	def test_get_orgtimerange_parsing_active(self):
		u"""
		get_orgdate should recognize all orgtimeranges in a given text
		"""
		daterangestr = u"<2011-09-12 Mon>--<2011-09-13 Tue>"
		result = get_orgdate(daterangestr)
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgTimeRange))
		self.assertEqual(unicode(result), daterangestr)
		self.assertTrue(result.active)

		daterangestr = u"<2011-09-12 Mon 10:20>--<2011-09-13 Tue 13:20>"
		result = get_orgdate(daterangestr)
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgTimeRange))
		self.assertEqual(unicode(result), daterangestr)
		self.assertTrue(result.active)

		daterangestr = u"<2011-09-12 Mon 10:20-13:20>"
		result = get_orgdate(daterangestr)
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgTimeRange))
		self.assertEqual(unicode(result), daterangestr)
		self.assertTrue(result.active)

	def test_get_orgdate_parsing_inactive(self):
		u"""
		get_orgdate should recognize all inactive orgdates in a given text
		"""
		result = get_orgdate(self.textinactive)
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertTrue(isinstance(get_orgdate(u"[2011-08-30 Tue]"), OrgDate))
		self.assertEqual(get_orgdate(u"[2011-08-30 Tue]").year, 2011)
		self.assertEqual(get_orgdate(u"[2011-08-30 Tue]").month, 8)
		self.assertEqual(get_orgdate(u"[2011-08-30 Tue]").day, 30)
		self.assertFalse(get_orgdate(u"[2011-08-30 Tue]").active)

		datestr = u"This date [2011-08-30 Tue] is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))

	def test_get_orgdatetime_parsing_passive(self):
		u"""
		get_orgdate should recognize all orgdatetimes in a given text
		"""
		result = get_orgdate(u"[2011-09-12 Mon 10:20]")
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDateTime))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 9)
		self.assertEqual(result.day, 12)
		self.assertEqual(result.hour, 10)
		self.assertEqual(result.minute, 20)
		self.assertFalse(result.active)

		result = get_orgdate(u"some datetime [2011-09-12 Mon 10:20] stuff")
		self.assertTrue(isinstance(result, OrgDateTime))

	def test_get_orgdate_parsing_with_list_of_texts(self):
		u"""
		get_orgdate should return the first date in the list.
		"""
		datelist = [u"<2011-08-29 Mon>"]
		result = get_orgdate(datelist)
		self.assertNotEquals(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = [u"<2011-08-29 Mon>",
				u"<2012-03-30 Fri>"]
		result = get_orgdate(datelist)
		self.assertNotEquals(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = [u"some <2011-08-29 Mon>text",
				u"<2012-03-30 Fri> is here"]
		result = get_orgdate(datelist)
		self.assertNotEquals(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = [u"here is no date",
				u"some <2011-08-29 Mon>text",
				u"<2012-03-30 Fri> is here"]
		result = get_orgdate(datelist)
		self.assertNotEquals(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)

		datelist = [u"here is no date",
				u"some <2011-08-29 Mon 20:10> text",
				u"<2012-03-30 Fri> is here"]
		result = get_orgdate(datelist)
		self.assertNotEquals(result, None)
		self.assertTrue(isinstance(result, OrgDateTime))
		self.assertEqual(result.year, 2011)
		self.assertEqual(result.month, 8)
		self.assertEqual(result.day, 29)
		self.assertEqual(result.hour, 20)
		self.assertEqual(result.minute, 10)

	def test_get_orgdate_parsing_with_invalid_input(self):
		self.assertEquals(get_orgdate(u"NONSENSE"), None)
		self.assertEquals(get_orgdate(u"No D<2011- Date 08-29 Mon>"), None)
		self.assertEquals(get_orgdate(u"2011-08-r9 Mon]"), None)
		self.assertEquals(get_orgdate(u"<2011-08-29 Mon"), None)
		self.assertEquals(get_orgdate(u"<2011-08-29 Mon]"), None)
		self.assertEquals(get_orgdate(u"2011-08-29 Mon"), None)
		self.assertEquals(get_orgdate(u"2011-08-29"), None)
		self.assertEquals(get_orgdate(u"2011-08-29 mon"), None)
		self.assertEquals(get_orgdate(u"<2011-08-29 mon>"), None)

		self.assertEquals(get_orgdate(u"wrong date embedded <2011-08-29 mon>"), None)
		self.assertEquals(get_orgdate(u"wrong date <2011-08-29 mon>embedded "), None)

	def test_get_orgdate_parsing_with_invalid_dates(self):
		u"""
		Something like <2011-14-29 Mon> (invalid dates, they don't exist)
		should not be parsed
		"""
		datestr = u"<2011-14-30 Tue>"
		self.assertEqual(get_orgdate(datestr), None)

		datestr = u"<2012-03-40 Tue>"
		self.assertEqual(get_orgdate(datestr), None)

		datestr = u"<2012-03-40 Tue 24:70>"
		self.assertEqual(get_orgdate(datestr), None)

	def test_get_orgdate_parsing_with_utf8(self):
		u"""
		get_orgdate should recognize all orgdates within a given utf-8 text
		"""
		result = get_orgdate(u'<2016-05-07 Sáb>')
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDate))
		self.assertEqual(result.year, 2016)
		self.assertEqual(result.month, 5)
		self.assertEqual(result.day, 7)
		self.assertTrue(result.active)

		datestr = u"This date <2016-05-07 Sáb> is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))

		result = get_orgdate(u'[2016-05-07 Sáb]')
		self.assertFalse(result.active)

		datestr = u"This date [2016-05-07 Sáb] is embedded"
		self.assertTrue(isinstance(get_orgdate(datestr), OrgDate))

	def test_get_orgdatetime_parsing_with_utf8(self):
		u"""
		get_orgdate should recognize all orgdatetimes in a given utf-8 text
		"""
		result = get_orgdate(u"<2016-05-07 Sáb 10:20>")
		self.assertNotEqual(result, None)
		self.assertTrue(isinstance(result, OrgDateTime))
		self.assertEqual(result.year, 2016)
		self.assertEqual(result.month, 5)
		self.assertEqual(result.day, 7)
		self.assertEqual(result.hour, 10)
		self.assertEqual(result.minute, 20)
		self.assertTrue(result.active)

		result = get_orgdate(u"some datetime <2016-05-07 Sáb 10:20> stuff")
		self.assertTrue(isinstance(result, OrgDateTime))

		result = get_orgdate(u"[2016-05-07 Sáb 10:20]")
		self.assertFalse(result.active)

		result = get_orgdate(u"some datetime [2016-05-07 Sáb 10:20] stuff")
		self.assertTrue(isinstance(result, OrgDateTime))



def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateParsingTestCase)

# vim: noexpandtab
