#!/usr/bin/env python
# -*- coding: utf-8 -*-

import test_vimbuffer

import test_libagendafilter
import test_libheading
import test_liborgdate
import test_liborgdatetime
import test_liborgtimerange
import test_liborgdate_parsing

import test_edit_structure
import test_misc
import test_navigator
import test_show_hide
import test_tags_properties
import test_todo
import test_date

import unittest


if __name__ == '__main__':
	tests = unittest.TestSuite()

	tests.addTests(test_vimbuffer.suite())

	# lib
	tests.addTests(test_libagendafilter.suite())
	tests.addTests(test_libheading.suite())
	tests.addTests(test_liborgdate.suite())
	tests.addTests(test_liborgdatetime.suite())
	tests.addTests(test_liborgtimerange.suite())
	tests.addTests(test_liborgdate_parsing.suite())

	# plugins
	tests.addTests(test_edit_structure.suite())
	tests.addTests(test_misc.suite())
	tests.addTests(test_navigator.suite())
	tests.addTests(test_show_hide.suite())
	tests.addTests(test_tags_properties.suite())
	tests.addTests(test_todo.suite())
	tests.addTests(test_date.suite())

	runner = unittest.TextTestRunner()
	runner.run(tests)

# vim: set noexpandtab:
