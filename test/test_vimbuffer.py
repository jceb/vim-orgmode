# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append('../ftplugin')

import vim

from orgmode.liborgmode import Heading
from orgmode.vimbuffer import VimBuffer

class VimBufferTestCase(unittest.TestCase):
	def setUp(self):
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				'exists("g:org_debug")': 0,
				'exists("g:org_debug")': 0,
				'exists("*repeat#set()")': 0,
				"v:count": 0}
		vim.current.buffer = """#Meta information
#more meta information
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		self.document = VimBuffer()

	def test_meta_information(self):
		# read meta information from document
		self.assertEqual('\n'.join(self.document.meta_information), '#Meta information\n#more meta information')
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 2)

		# assign meta information directly to an element in array
		self.document.meta_information[0] = '#More or less meta information'
		self.assertEqual('\n'.join(self.document.meta_information), '#More or less meta information\n#more meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].start, 2)

		# assign a single line string
		self.document.meta_information = '#Less meta information'
		self.assertEqual('\n'.join(self.document.meta_information), '#Less meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].start, 1)

		# assign a multi line string
		self.document.meta_information = '#Less meta information\n#lesser information'
		self.assertEqual('\n'.join(self.document.meta_information), '#Less meta information\n#lesser information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].start, 2)

		# assign a single element array of strings
		self.document.meta_information = '#More or less meta information'.split('\n')
		self.assertEqual('\n'.join(self.document.meta_information), '#More or less meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].start, 1)

		# assign a multi element array of strings
		self.document.meta_information = '#More or less meta information\n#lesser information'.split('\n')
		self.assertEqual('\n'.join(self.document.meta_information), '#More or less meta information\n#lesser information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].start, 2)

		vim.current.buffer = """* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		self.document = VimBuffer()

		# read no meta information from document
		self.assertEqual(self.document.meta_information, [])
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.is_dirty, False)

		# assign meta information to a former empty field
		self.document.meta_information = '#More or less meta information\n#lesser information'.split('\n')
		self.assertEqual('\n'.join(self.document.meta_information), '#More or less meta information\n#lesser information')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.is_dirty, True)

		# assign an empty array as meta information
		self.document.meta_information = []
		self.assertEqual(self.document.meta_information, [])
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.is_dirty, True)

		# assign an empty string as meta information
		self.document.meta_information = ''
		self.assertEqual(self.document.meta_information, [''])
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.is_dirty, True)

	def test_bufnr(self):
		self.assertEqual(self.document.bufnr, 0)
		# TODO add more tests as soon as multi buffer support has been implemented

	def test_write_meta_information(self):
		# write nothing
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.write(), False)
		self.assertEqual('\n'.join(self.document.meta_information), '#Meta information\n#more meta information')

		# write changed meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = '#More or less meta information\n#lesser information'.split('\n')
		self.assertEqual('\n'.join(self.document.meta_information), '#More or less meta information\n#lesser information')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual('\n'.join(VimBuffer().meta_information), '#More or less meta information\n#lesser information')

		# shorten meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = '!More or less meta information'.split('\n')
		self.assertEqual('\n'.join(self.document.meta_information), '!More or less meta information')
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.headings[0]._orig_start, 1)
		self.assertEqual('\n'.join(VimBuffer().meta_information), '!More or less meta information')

		# lengthen meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = '!More or less meta information\ntest\ntest'
		self.assertEqual('\n'.join(self.document.meta_information), '!More or less meta information\ntest\ntest')
		self.assertEqual(self.document.headings[0].start, 3)
		self.assertEqual(self.document.headings[0]._orig_start, 1)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 3)
		self.assertEqual(self.document.headings[0]._orig_start, 3)
		self.assertEqual('\n'.join(VimBuffer().meta_information), '!More or less meta information\ntest\ntest')

		# write empty meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = []
		self.assertEqual(self.document.meta_information, [])
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.headings[0]._orig_start, 3)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.headings[0]._orig_start, 0)
		self.assertEqual(VimBuffer().meta_information, [])

	def test_write_changed_title_and_body(self):
		# write a changed title
		self.document.headings[0].title = 'Heading 1'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].title, 'Heading 1')
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(VimBuffer().headings[0].title, 'Heading 1')

		# write a changed body
		self.assertEqual(self.document.headings[0].end, 5)
		self.document.headings[0].body[0] = 'Another text'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].body, ['Another text', '', 'Bla bla'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(VimBuffer().headings[0].body, ['Another text', '', 'Bla bla'])

		# write a shortened body
		self.document.headings[0].body = 'Another text'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].end, 3)
		self.assertEqual(len(self.document.headings[0]), 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 4)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].body, ['Another text'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 3)
		self.assertEqual(len(self.document.headings[0]), 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 2)
		self.assertEqual(self.document.headings[0].children[0].start, 4)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 4)
		self.assertEqual(VimBuffer().headings[0].body, ['Another text'])

		# write a lengthened body
		self.document.headings[0].body = ['Another text', 'more', 'and more', 'and more']
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].end, 6)
		self.assertEqual(len(self.document.headings[0]), 5)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 2)
		self.assertEqual(self.document.headings[0].children[0].start, 7)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 4)
		self.assertEqual(self.document.headings[0].body, ['Another text', 'more', 'and more', 'and more'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 6)
		self.assertEqual(len(self.document.headings[0]), 5)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 5)
		self.assertEqual(self.document.headings[0].children[0].start, 7)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 7)
		self.assertEqual(VimBuffer().headings[0].body, ['Another text', 'more', 'and more', 'and more'])

	def test_write_delete_heading(self):
		# delete a heading
		self.assertEqual(len(self.document.headings[0].children), 2)
		del self.document.headings[0].children[0]
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings[0].children), 1)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 10)
		self.assertEqual(self.document.headings[0].children[0]._orig_len, 3)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_len, 3)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(self.document.headings[0].children), 1)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(d.headings[0].end, 5)
		self.assertEqual(len(d.headings[0]), 4)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0]._orig_len, 4)
		self.assertEqual(d.headings[0].children[0].start, 6)
		self.assertEqual(d.headings[0].children[0]._orig_start, 6)
		self.assertEqual(d.headings[0].children[0]._orig_len, 3)

	def test_write_delete_first_heading(self):
		# delete the first heading
		self.assertEqual(len(self.document.headings), 3)
		del self.document.headings[0]
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(self.document.headings[0].end, 2)
		self.assertEqual(len(self.document.headings[0]), 1)
		self.assertEqual(self.document.headings[0]._orig_start, 17)
		self.assertEqual(self.document.headings[0]._orig_len, 1)
		self.assertEqual(self.document.headings[1].start, 3)
		self.assertEqual(self.document.headings[1]._orig_start, 18)
		self.assertEqual(self.document.headings[1]._orig_len, 3)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 2)
		self.assertEqual(len(self.document.headings[0]), 1)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 1)
		self.assertEqual(self.document.headings[1].start, 3)
		self.assertEqual(self.document.headings[1]._orig_start, 3)
		self.assertEqual(self.document.headings[1]._orig_len, 3)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(d.headings[0].end, 2)
		self.assertEqual(len(d.headings[0]), 1)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0]._orig_len, 1)
		self.assertEqual(d.headings[1].start, 3)
		self.assertEqual(d.headings[1]._orig_start, 3)
		self.assertEqual(d.headings[1]._orig_len, 3)

	def test_write_delete_last_heading(self):
		# delete the last heading
		self.assertEqual(len(self.document.headings), 3)
		del self.document.headings[-1]
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(self.document.headings[0].end_of_last_child, 16)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[-1].start, 17)
		self.assertEqual(self.document.headings[-1]._orig_start, 17)
		self.assertEqual(self.document.headings[-1]._orig_len, 1)
		self.assertEqual(self.document.headings[-1].end, 17)
		self.assertEqual(self.document.headings[-1].end_of_last_child, 17)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(self.document.headings[0].end_of_last_child, 16)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[-1].start, 17)
		self.assertEqual(self.document.headings[-1]._orig_start, 17)
		self.assertEqual(self.document.headings[-1]._orig_len, 1)
		self.assertEqual(self.document.headings[-1].end, 17)
		self.assertEqual(self.document.headings[-1].end_of_last_child, 17)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(d.headings[0].end, 5)
		self.assertEqual(d.headings[0].end_of_last_child, 16)
		self.assertEqual(len(d.headings[0]), 4)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0]._orig_len, 4)
		self.assertEqual(d.headings[-1].start, 17)
		self.assertEqual(d.headings[-1]._orig_start, 17)
		self.assertEqual(d.headings[-1]._orig_len, 1)
		self.assertEqual(d.headings[-1].end, 17)
		self.assertEqual(d.headings[-1].end_of_last_child, 17)

	def test_write_delete_multiple_headings(self):
		# delete multiple headings
		self.assertEqual(len(self.document.headings), 3)
		del self.document.headings[1]
		del self.document.headings[0].children[1].children[0]
		del self.document.headings[0].children[0]
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(len(self.document.headings[0].children), 1)
		self.assertEqual(len(self.document.headings[0].children[0].children), 1)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(self.document.headings[0].end_of_last_child, 9)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 10)
		self.assertEqual(self.document.headings[0].children[0].children[0]._orig_start, 16)
		self.assertEqual(self.document.headings[-1]._orig_start, 18)
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0].children[0].start, 9)
		self.assertEqual(self.document.headings[-1].start, 10)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(self.document.headings[0].end_of_last_child, 9)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].children[0].children[0]._orig_start, 9)
		self.assertEqual(self.document.headings[-1]._orig_start, 10)
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0].children[0].start, 9)
		self.assertEqual(self.document.headings[-1].start, 10)
		self.assertEqual(self.document.headings[0].title, 'Überschrift 1')
		self.assertEqual(self.document.headings[0].children[0].title, 'Überschrift 1.2')
		self.assertEqual(self.document.headings[0].children[0].children[0].title, 'Überschrift 1.2.1')
		self.assertEqual(self.document.headings[-1].title, 'Überschrift 3')

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(self.document.headings), 2)
		self.assertEqual(len(self.document.headings[0].children), 1)
		self.assertEqual(len(self.document.headings[0].children[0].children), 1)
		self.assertEqual(d.headings[0].end, 5)
		self.assertEqual(d.headings[0].end_of_last_child, 9)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0].children[0]._orig_start, 6)
		self.assertEqual(d.headings[0].children[0].children[0]._orig_start, 9)
		self.assertEqual(d.headings[-1]._orig_start, 10)
		self.assertEqual(d.headings[0].start, 2)
		self.assertEqual(d.headings[0].children[0].start, 6)
		self.assertEqual(d.headings[0].children[0].children[0].start, 9)
		self.assertEqual(d.headings[-1].start, 10)
		self.assertEqual(d.headings[0].title, 'Überschrift 1')
		self.assertEqual(d.headings[0].children[0].title, 'Überschrift 1.2')
		self.assertEqual(d.headings[0].children[0].children[0].title, 'Überschrift 1.2.1')
		self.assertEqual(d.headings[-1].title, 'Überschrift 3')


	def test_write_add_heading(self):
		# add a heading
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children), 2)
		h = Heading()
		h.title = 'Test heading'
		h.level = 2
		h.body = 'Text, text\nmore text'
		self.document.headings[0].children.append(h)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings[0].children), 3)
		self.assertEqual(self.document.headings[0].children[-1].title, 'Test heading')

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(len(self.document.headings[0].children), 3)
		self.assertEqual(self.document.headings[0].children[-1].title, 'Test heading')

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(d.headings[0].children), 3)
		self.assertEqual(d.headings[0].children[-1].title, 'Test heading')

	def test_write_add_heading_before_first_heading(self):
		# add a heading before the first heading
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = 'Test heading'
		h.level = 2
		h.body = 'Text, text\nmore text'
		self.assertEqual(h.start, None)
		self.document.headings[0:0] = h
		self.assertEqual(h.start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 4)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].title, 'Test heading')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(len(self.document.headings[0]), 3)
		self.assertEqual(self.document.headings[1].title, 'Überschrift 1')
		self.assertEqual(self.document.headings[1].start, 5)
		self.assertEqual(len(self.document.headings[1]), 4)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(d.headings), 4)
		self.assertEqual(d.headings[0].title, 'Test heading')
		self.assertEqual(d.headings[0].start, 2)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(len(d.headings[0]), 3)
		self.assertEqual(d.headings[1].title, 'Überschrift 1')
		self.assertEqual(d.headings[1].start, 5)
		self.assertEqual(len(d.headings[1]), 4)

	def test_write_add_heading_after_last_heading_toplevel(self):
		# add a heading after the last heading (top level heading)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = 'Test heading'
		h.body = 'Text, text\nmore text'
		self.assertEqual(h.start, None)
		self.document.headings += h
		self.assertEqual(h.start, 21)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 4)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[-1].title, 'Test heading')
		self.assertEqual(self.document.headings[-1].start, 21)
		self.assertEqual(self.document.headings[-1]._orig_start, 21)
		self.assertEqual(len(self.document.headings[-1]), 3)
		self.assertEqual(self.document.headings[-2].title, 'Überschrift 3')
		self.assertEqual(self.document.headings[-2].start, 18)
		self.assertEqual(len(self.document.headings[-2]), 3)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(d.headings), 4)
		self.assertEqual(d.headings[-1].title, 'Test heading')
		self.assertEqual(d.headings[-1].start, 21)
		self.assertEqual(d.headings[-1]._orig_start, 21)
		self.assertEqual(len(d.headings[-1]), 3)
		self.assertEqual(d.headings[-2].title, 'Überschrift 3')
		self.assertEqual(d.headings[-2].start, 18)
		self.assertEqual(len(d.headings[-2]), 3)

	def test_write_add_heading_after_last_heading_subheading(self):
		# add a heading after the last heading (subheading)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = 'Test heading'
		h.level = 2
		h.body = 'Text, text\nmore text'
		self.assertEqual(h.start, None)
		self.document.headings[-1].children += h
		self.assertEqual(h.start, 21)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[-1]), 3)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[-1].children[-1].title, 'Test heading')
		self.assertEqual(self.document.headings[-1].children[-1].start, 21)
		self.assertEqual(self.document.headings[-1].children[-1]._orig_start, 21)
		self.assertEqual(len(self.document.headings[-1].children[-1]), 3)
		self.assertEqual(self.document.headings[-1].title, 'Überschrift 3')
		self.assertEqual(self.document.headings[-1].start, 18)
		self.assertEqual(len(self.document.headings[-1]), 3)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(d.headings), 3)
		self.assertEqual(len(d.headings[-1]), 3)
		self.assertEqual(d.headings[-1].children[-1].title, 'Test heading')
		self.assertEqual(d.headings[-1].children[-1].start, 21)
		self.assertEqual(d.headings[-1].children[-1]._orig_start, 21)
		self.assertEqual(len(d.headings[-1].children[-1]), 3)
		self.assertEqual(d.headings[-1].title, 'Überschrift 3')
		self.assertEqual(d.headings[-1].start, 18)
		self.assertEqual(len(d.headings[-1]), 3)

	def test_write_replace_one_heading(self):
		# replace subheadings by a list of newly created headings (one item)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = 'Test heading'
		h.level = 3
		h.body = 'Text, text\nmore text\nanother text'
		self.assertEqual(h.start, None)
		self.document.headings[0].children[1].children[0] = h
		self.assertEqual(h.start, 13)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children[1].children), 2)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].children[1].children[0].title, 'Test heading')
		self.assertEqual(self.document.headings[0].children[1].children[0].start, 13)
		self.assertEqual(self.document.headings[0].children[1].children[0]._orig_start, 13)
		self.assertEqual(len(self.document.headings[0].children[1].children[0]), 4)
		self.assertEqual(len(self.document.headings[0].children[1]), 3)
		self.assertEqual(len(self.document.headings[0].children[0].children), 0)
		self.assertEqual(len(self.document.headings[1].children), 0)
		self.assertEqual(self.document.headings[0].children[1].children[-1].title, 'Überschrift 1.2.1')
		self.assertEqual(self.document.headings[0].children[1].children[-1].start, 17)

		# sanity check
		d = VimBuffer()
		self.assertEqual(len(d.headings), 3)
		self.assertEqual(len(d.headings[0].children[1].children), 2)
		self.assertEqual(d.headings[0].children[1].children[0].title, 'Test heading')
		self.assertEqual(d.headings[0].children[1].children[0].start, 13)
		self.assertEqual(d.headings[0].children[1].children[0]._orig_start, 13)
		self.assertEqual(len(d.headings[0].children[1].children[0]), 4)
		self.assertEqual(len(d.headings[0].children[1]), 3)
		self.assertEqual(len(d.headings[0].children[0].children), 0)
		self.assertEqual(len(d.headings[1].children), 0)
		self.assertEqual(d.headings[0].children[1].children[-1].title, 'Überschrift 1.2.1')
		self.assertEqual(d.headings[0].children[1].children[-1].start, 17)

	def test_dom(self):
		self.assertEqual(len(self.document.headings), 3)
		for h in self.document.headings:
			self.assertEqual(h.level, 1)
		self.assertEqual(len(self.document.headings[0].children), 2)
		self.assertEqual(len(self.document.headings[0].children[0].children), 0)
		self.assertEqual(len(self.document.headings[0].children[1].children), 2)
		self.assertEqual(len(self.document.headings[0].children[1].children[0].children), 0)
		self.assertEqual(len(self.document.headings[0].children[1].children[1].children), 0)
		self.assertEqual(len(self.document.headings[1].children), 0)
		self.assertEqual(len(self.document.headings[2].children), 0)

		# test no heading
		vim.current.window.cursor = (1, 0)
		h = self.document.current_heading()
		self.assertEqual(h, None)

	def test_index_boundaries(self):
		# test index boundaries
		vim.current.window.cursor = (-1, 0)
		h = self.document.current_heading()
		self.assertEqual(h, None)

		vim.current.window.cursor = (21, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(h.start, 18)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.next_sibling, None)
		self.assertEqual(len(h.children), 0)

		vim.current.window.cursor = (999, 0)
		h = self.document.current_heading()
		self.assertEqual(h, None)

	def test_heading_start_and_end(self):
		# test heading start and end
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 2)
		self.assertEqual(h.end, 5)
		self.assertEqual(h.end_of_last_child, 16)

		vim.current.window.cursor = (12, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 10)
		self.assertEqual(h.end, 12)
		self.assertEqual(h.end_of_last_child, 16)

		vim.current.window.cursor = (19, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.start, 18)
		self.assertEqual(h.end, 20)
		self.assertEqual(h.end_of_last_child, 20)

		vim.current.buffer = """
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split('\n')
		self.document = VimBuffer()
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 2)
		self.assertEqual(h.title, 'Überschrift 1.2')
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.children[1].start, 7)
		self.assertEqual(h.children[1].children, [])
		self.assertEqual(h.children[1].next_sibling, None)
		self.assertEqual(h.children[1].end, 7)
		self.assertEqual(h.start, 1)
		self.assertEqual(h.end, 3)
		self.assertEqual(h.end_of_last_child, 7)

		vim.current.buffer = """
* Überschrift 2
* Überschrift 3""".split('\n')
		self.document = VimBuffer()
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.end, 2)
		self.assertEqual(h.end_of_last_child, 2)
		self.assertEqual(h.title, 'Überschrift 3')

	def test_first_heading(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 1)
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.previous_sibling, None)

		self.assertEqual(h.children[0].level, 2)
		self.assertEqual(h.children[0].children, [])
		self.assertEqual(h.children[1].level, 2)
		self.assertEqual(len(h.children[1].children), 2)
		self.assertEqual(h.children[1].children[0].level, 4)
		self.assertEqual(h.children[1].children[1].level, 3)

		self.assertEqual(h.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.level, 1)

		self.assertEqual(h.next_sibling.next_sibling.next_sibling, None)
		self.assertEqual(h.next_sibling.next_sibling.parent, None)

	def test_heading_in_the_middle(self):
		# test heading in the middle of the file
		vim.current.window.cursor = (14, 0)
		h = self.document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 4)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.next_sibling, None)
		self.assertNotEqual(h.next_sibling.previous_sibling, None)
		self.assertEqual(h.next_sibling.level, 3)
		self.assertEqual(h.previous_sibling, None)

	def test_previous_headings(self):
		# test previous headings
		vim.current.window.cursor = (17, 0)
		h = self.document.current_heading()

		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 3)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.parent.level, 2)
		self.assertNotEqual(h.parent.previous_sibling, None)
		self.assertNotEqual(h.previous_sibling.parent, None)
		self.assertEqual(h.previous_sibling.parent.start, 10)

		vim.current.window.cursor = (14, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h.parent, None)
		self.assertEqual(h.parent.start, 10)

		vim.current.window.cursor = (21, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.level, 1)
		self.assertNotEqual(h.previous_sibling, None)
		self.assertEqual(h.previous_sibling.level, 1)
		self.assertNotEqual(h.previous_sibling.previous_sibling, None)
		self.assertEqual(h.previous_sibling.previous_sibling.level, 1)
		self.assertEqual(h.previous_sibling.previous_sibling.previous_sibling,
                None)

		vim.current.window.cursor = (77, 0)
		h = self.document.current_heading()
		self.assertEqual(h, None)

		# test heading extractor
		#self.assertEqual(h.heading, 'Überschrift 1')
		#self.assertEqual(h.title, 'Text 1\n\nBla bla')

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(VimBufferTestCase)
