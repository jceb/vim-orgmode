#!/usr/bin/env python
# -*- coding: utf-8 -*-

import test_edit_structure
import test_headings
import test_misc
import test_navigator
import test_show_hide
import test_tags_properties
import test_todo

import unittest

if __name__ == '__main__':
	tests = unittest.TestSuite([
		test_edit_structure.suite(),
		test_headings.suite(),
		test_misc.suite(),
		test_navigator.suite(),
		test_show_hide.suite(),
		test_tags_properties.suite(),
		test_todo.suite()])
	runner = unittest.TextTestRunner()
	runner.run(tests)
