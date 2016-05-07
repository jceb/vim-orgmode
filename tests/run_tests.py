#!/usr/bin/env python
# -*- coding: utf-8 -*-

import test_vimbuffer

import test_libagendafilter
import test_libcheckbox
import test_libbase
import test_libheading
import test_liborgdate
import test_liborgdate_utf8
import test_liborgdate_parsing
import test_liborgdatetime
import test_liborgtimerange

import test_plugin_date
import test_plugin_edit_structure
import test_plugin_edit_checkbox
import test_plugin_misc
import test_plugin_navigator
import test_plugin_show_hide
import test_plugin_tags_properties
import test_plugin_todo
import test_plugin_mappings

import unittest


if __name__ == '__main__':
	tests = unittest.TestSuite()

	tests.addTests(test_vimbuffer.suite())

	# lib
	tests.addTests(test_libbase.suite())
	tests.addTests(test_libcheckbox.suite())
	tests.addTests(test_libagendafilter.suite())
	tests.addTests(test_libheading.suite())
	tests.addTests(test_liborgdate.suite())
	tests.addTests(test_liborgdate_utf8.suite())
	tests.addTests(test_liborgdate_parsing.suite())
	tests.addTests(test_liborgdatetime.suite())
	tests.addTests(test_liborgtimerange.suite())

	# plugins
	tests.addTests(test_plugin_date.suite())
	tests.addTests(test_plugin_edit_structure.suite())
	tests.addTests(test_plugin_edit_checkbox.suite())
	tests.addTests(test_plugin_misc.suite())
	tests.addTests(test_plugin_navigator.suite())
	tests.addTests(test_plugin_show_hide.suite())
	tests.addTests(test_plugin_tags_properties.suite())
	tests.addTests(test_plugin_todo.suite())
	tests.addTests(test_plugin_mappings.suite())

	runner = unittest.TextTestRunner()
	runner.run(tests)

# vim: set noexpandtab:
