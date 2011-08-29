# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

#from datetime import date
#from datetime import datetime

#from orgmode.plugins.Date import Date


class OrgDateTestCase(unittest.TestCase):
	u"""
    Tests all the functionality of the OrgDate
	"""

	def setUp(self):
		pass

	def test(self):
		pass


def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateTestCase)

# vi: noexpandtab
