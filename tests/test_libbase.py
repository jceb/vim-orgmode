# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from orgmode.liborgmode.base import Direction, get_domobj_range
from orgmode.liborgmode.headings import Heading


class LibBaseTestCase(unittest.TestCase):

	def setUp(self):
		self.case1 = """
* head1
 heading body
 for testing
* head2
** head3
		""".split("\n")

	def test_base_functions(self):
		# direction FORWARD
		(start, end) = get_domobj_range(content=self.case1, position=1, identify_fun=Heading.identify_heading)
		self.assertEqual((start, end), (1, 3))
		(start, end) = get_domobj_range(content=self.case1, position=3, direction=Direction.BACKWARD, \
										identify_fun=Heading.identify_heading)
		self.assertEqual((start, end), (1, 3))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(
			LibBaseTestCase)

# vim: set noexpandtab:
