# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim
import os.path

from orgmode._vim import ORGMODE

PLUGIN_NAME = u'BabelTangle'

counter = 0

class BabelTangleTestCase(unittest.TestCase):

	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.current.buffer[:] = [ i.encode(u'utf-8') for i in u"""
* Heading 1
  This is some text, followed by a source block

  #+BEGIN_SRC sh :tangle tmp_tangle_fileoutput
    print -- "Everything ok!"
  #+END_SRC
""".split(u'\n') ]

	def test_tangling(self):
		global counter
		counter += 1
		# test on self.c1
		# update_checkboxes_status
                vim.command("OrgBabelTangle")
                self.assertTrue(os.path.isfile("tmp_tangle_fileoutput"))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(BabelTangleTestCase)

# vim: set noexpandtab
