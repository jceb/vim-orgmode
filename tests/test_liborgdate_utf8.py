# -*- coding: utf-8 -*-

import sys
import unittest
import locale
import threading

from datetime import date
from contextlib import contextmanager

from orgmode.py3compat.unicode_compatibility import *

sys.path.append(u'../ftplugin')
from orgmode.liborgmode.orgdate import OrgDate

class OrgDateUtf8TestCase(unittest.TestCase):
	u"""
	Tests OrgDate with utf-8 enabled locales
	"""
	LOCALE_LOCK = threading.Lock()
	UTF8_LOCALE = "pt_BR.utf-8"

	@contextmanager
	def setlocale(self, name):
		with self.LOCALE_LOCK:
			saved = locale.setlocale(locale.LC_ALL)
			try:
				yield locale.setlocale(locale.LC_ALL, name)
			finally:
				locale.setlocale(locale.LC_ALL, saved)

	def setUp(self):
		self.year = 2016
		self.month = 5
		self.day = 7
		self.text = u'<2016-05-07 Sáb>'
		self.textinactive = u'[2016-05-07 Sáb]'

	def test_OrdDate_str_unicode_active(self):
		with self.setlocale(self.UTF8_LOCALE):
			od = OrgDate(True, self.year, self.month, self.day)
			self.assertEqual(self.text, unicode(od))

	def test_OrdDate_str_unicode_inactive(self):
		with self.setlocale(self.UTF8_LOCALE):
			od = OrgDate(False, self.year, self.month, self.day)
			self.assertEqual(self.textinactive, unicode(od))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(OrgDateUtf8TestCase)

# vi: noexpandtab
