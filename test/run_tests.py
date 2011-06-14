#!/usr/bin/env python
# -*- coding: utf-8 -*-

import test_vimbuffer
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
	tests.addTests(test_edit_structure.suite())
	tests.addTests(test_misc.suite())
	tests.addTests(test_navigator.suite())
	tests.addTests(test_show_hide.suite())
	tests.addTests(test_tags_properties.suite())
	tests.addTests(test_todo.suite())
	tests.addTests(test_date.suite())

	runner = unittest.TextTestRunner()
	runner.run(tests)
