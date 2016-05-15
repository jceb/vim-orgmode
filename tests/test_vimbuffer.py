# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

import vim

from orgmode.liborgmode.headings import Heading
from orgmode.vimbuffer import VimBuffer

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *

counter = 0
class VimBufferTestCase(unittest.TestCase):
	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'),
									   u_encode(u'DONE'), u_encode(u'|')],
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u'&ts'): u_encode(u'8'),
				u_encode(u'exists("g:org_tag_column")'): u_encode(u'0'),
				u_encode(u'exists("b:org_tag_column")'): u_encode(u'0'),
				u_encode(u"v:count"): u_encode(u'0')}
		vim.current.buffer[:] = [u_encode(i) for i in u"""#Meta information
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
""".split(u'\n') ]
		self.document = VimBuffer().init_dom()

	def test_write_heading_tags(self):
		self.assertEqual(self.document.is_dirty, False)
		h = self.document.find_heading()
		self.assertEqual(h._orig_start, 2)
		self.assertEqual(h.title, u'Überschrift 1')
		h.tags = [u'test', u'tag']
		self.assertEqual(h.tags[0], u'test')
		self.document.write_heading(h)

		# sanity check
		d = VimBuffer().init_dom()
		h2 = self.document.find_heading()
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(len(d.headings[0].tags), 2)
		self.assertEqual(d.headings[0].tags[0], u'test')
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0].children[0]._orig_start, 6)

	def test_write_multi_heading_bodies(self):
		self.assertEqual(self.document.is_dirty, False)
		h = self.document.headings[0].copy()
		self.assertEqual(h._orig_start, 2)
		self.assertEqual(h.title, u'Überschrift 1')
		h.body.append(u'test')
		h.children[0].body.append(u'another line')
		self.document.write_heading(h)

		# sanity check
		d = VimBuffer().init_dom()
		h2 = self.document.find_heading()
		self.assertEqual(len(d.headings[0].body), 4)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(d.headings[0].children[0]._orig_start, 7)
		self.assertEqual(d.headings[0].children[0].title, u'Überschrift 1.1')
		self.assertEqual(len(d.headings[0].children[0].body), 4)
		self.assertEqual(d.headings[0].children[1]._orig_start, 12)
		self.assertEqual(d.headings[0].children[1].title, u'Überschrift 1.2')
		self.assertEqual(len(d.headings[0].children[1].body), 2)

	def test_meta_information_assign_directly(self):
		# read meta information from document
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#Meta information\n#more meta information')
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 2)

		# assign meta information directly to an element in array
		self.document.meta_information[0] = u'#More or less meta information'
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#More or less meta information\n#more meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, True)
		self.assertEqual(self.document.headings[0].start, 2)

	def test_meta_information_assign_string(self):
		# assign a single line string
		self.document.meta_information = u'#Less meta information'
		self.assertEqual('\n'.join(self.document.meta_information), u'#Less meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, True)
		self.assertEqual(self.document.headings[0].start, 1)

	def test_meta_information_assign_multi_line_string(self):
		# assign a multi line string
		self.document.meta_information = u'#Less meta information\n#lesser information'
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#Less meta information\n#lesser information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, True)
		self.assertEqual(self.document.headings[0].start, 2)

	def test_meta_information_assign_one_element_array(self):
		# assign a single element array of strings
		self.document.meta_information = u'#More or less meta information'.split(u'\n')
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#More or less meta information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, True)
		self.assertEqual(self.document.headings[0].start, 1)

	def test_meta_information_assign_multi_element_array(self):
		# assign a multi element array of strings
		self.document.meta_information = u'#More or less meta information\n#lesser information'.split(u'\n')
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#More or less meta information\n#lesser information')
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, True)
		self.assertEqual(self.document.headings[0].start, 2)

	def test_meta_information_read_no_meta_information(self):
		vim.current.buffer[:] = [ u_encode(i) for i in u"""* Überschrift 1
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
""".split(u'\n') ]
		self.document = VimBuffer().init_dom()

		# read no meta information from document
		self.assertEqual(self.document.meta_information, [])
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.is_dirty, False)

		# assign meta information to a former empty field
		self.document.meta_information = u'#More or less meta information\n#lesser information'.split('\n')
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#More or less meta information\n#lesser information')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.is_dirty, True)

	def test_meta_information_assign_empty_array(self):
		# assign an empty array as meta information
		self.document.meta_information = []
		self.assertEqual(self.document.meta_information, [])
		self.assertEqual(self.document.headings[0].start, 0)
		self.assertEqual(self.document.is_dirty, True)

	def test_meta_information_assign_empty_string(self):
		# assign an empty string as meta information
		self.document.meta_information = u''
		self.assertEqual(self.document.meta_information, [u''])
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.is_dirty, True)

	def test_bufnr(self):
		self.assertEqual(self.document.bufnr, vim.current.buffer.number)
		# TODO add more tests as soon as multi buffer support has been implemented

	def test_write_meta_information(self):
		# write nothing
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.write(), False)
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#Meta information\n#more meta information')

		# write changed meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = u'#More or less meta information\n#lesser information'.split('\n')
		self.assertEqual(u'\n'.join(self.document.meta_information), u'#More or less meta information\n#lesser information')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(u'\n'.join(VimBuffer().init_dom().meta_information), u'#More or less meta information\n#lesser information')

		# shorten meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = u'!More or less meta information'.split(u'\n')
		self.assertEqual(u'\n'.join(self.document.meta_information), u'!More or less meta information')
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 1)
		self.assertEqual(self.document.headings[0]._orig_start, 1)
		self.assertEqual(u'\n'.join(VimBuffer().init_dom().meta_information), u'!More or less meta information')

		# lengthen meta information
		self.assertEqual(self.document.is_dirty, False)
		self.document.meta_information = u'!More or less meta information\ntest\ntest'
		self.assertEqual(u'\n'.join(self.document.meta_information), u'!More or less meta information\ntest\ntest')
		self.assertEqual(self.document.headings[0].start, 3)
		self.assertEqual(self.document.headings[0]._orig_start, 1)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].start, 3)
		self.assertEqual(self.document.headings[0]._orig_start, 3)
		self.assertEqual(u'\n'.join(VimBuffer().init_dom().meta_information), u'!More or less meta information\ntest\ntest')

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
		self.assertEqual(VimBuffer().init_dom().meta_information, [])

	def test_write_changed_title(self):
		# write a changed title
		self.document.headings[0].title = u'Heading 1'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, False)
		self.assertEqual(self.document.headings[0].is_dirty_body, False)
		self.assertEqual(self.document.headings[0].is_dirty_heading, True)
		self.assertEqual(self.document.headings[0].title, u'Heading 1')
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
		self.assertEqual(VimBuffer().init_dom().headings[0].title, u'Heading 1')

	def test_write_changed_body(self):
		# write a changed body
		self.assertEqual(self.document.headings[0].end, 5)
		self.document.headings[0].body[0] = u'Another text'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, False)
		self.assertEqual(self.document.headings[0].is_dirty_body, True)
		self.assertEqual(self.document.headings[0].is_dirty_heading, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].body, [u'Another text', u'', u'Bla bla'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 5)
		self.assertEqual(len(self.document.headings[0]), 4)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 6)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(VimBuffer().init_dom().headings[0].body, [u'Another text', u'', u'Bla bla'])

	def test_write_shortened_body(self):
		# write a shortened body
		self.document.headings[0].body = u'Another text'
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, False)
		self.assertEqual(self.document.headings[0].is_dirty_body, True)
		self.assertEqual(self.document.headings[0].is_dirty_heading, False)
		self.assertEqual(self.document.headings[0].end, 3)
		self.assertEqual(len(self.document.headings[0]), 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 4)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].body, [u'Another text'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 3)
		self.assertEqual(len(self.document.headings[0]), 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 2)
		self.assertEqual(self.document.headings[0].children[0].start, 4)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 4)
		self.assertEqual(VimBuffer().init_dom().headings[0].body, [u'Another text'])

	def test_write_lengthened_body(self):
		# write a lengthened body
		self.document.headings[0].body = [u'Another text', u'more', u'and more', u'and more']
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.is_dirty_meta_information, False)
		self.assertEqual(self.document.headings[0].is_dirty_body, True)
		self.assertEqual(self.document.headings[0].is_dirty_heading, False)
		self.assertEqual(self.document.headings[0].end, 6)
		self.assertEqual(len(self.document.headings[0]), 5)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 4)
		self.assertEqual(self.document.headings[0].children[0].start, 7)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 6)
		self.assertEqual(self.document.headings[0].body, [u'Another text', u'more', u'and more', u'and more'])

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].end, 6)
		self.assertEqual(len(self.document.headings[0]), 5)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(self.document.headings[0]._orig_len, 5)
		self.assertEqual(self.document.headings[0].children[0].start, 7)
		self.assertEqual(self.document.headings[0].children[0]._orig_start, 7)
		self.assertEqual(VimBuffer().init_dom().headings[0].body, [u'Another text', u'more', u'and more', u'and more'])

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
		d = VimBuffer().init_dom()
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
		d = VimBuffer().init_dom()
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
		d = VimBuffer().init_dom()
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
		self.assertEqual(self.document.headings[0].title, u'Überschrift 1')
		self.assertEqual(self.document.headings[0].children[0].title, u'Überschrift 1.2')
		self.assertEqual(self.document.headings[0].children[0].children[0].title, u'Überschrift 1.2.1')
		self.assertEqual(self.document.headings[-1].title, u'Überschrift 3')

		# sanity check
		d = VimBuffer().init_dom()
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
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(d.headings[0].children[0].title, u'Überschrift 1.2')
		self.assertEqual(d.headings[0].children[0].children[0].title, u'Überschrift 1.2.1')
		self.assertEqual(d.headings[-1].title, u'Überschrift 3')


	def test_write_add_heading(self):
		# add a heading
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children), 2)
		h = Heading()
		h.title = u'Test heading'
		h.level = 2
		h.body = u'Text, text\nmore text'
		self.document.headings[0].children.append(h)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings[0].children), 3)
		self.assertEqual(self.document.headings[0].children[-1].title, u'Test heading')

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(len(self.document.headings[0].children), 3)
		self.assertEqual(self.document.headings[0].children[-1].title, u'Test heading')

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings[0].children), 3)
		self.assertEqual(d.headings[0].children[-1].title, u'Test heading')

	def test_write_add_heading_before_first_heading(self):
		# add a heading before the first heading
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.level = 2
		h.body = u'Text, text\nmore text'
		self.assertEqual(h.start, None)
		self.document.headings[0:0] = h
		self.assertEqual(h.start, 2)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 4)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].title, u'Test heading')
		self.assertEqual(self.document.headings[0].start, 2)
		self.assertEqual(self.document.headings[0]._orig_start, 2)
		self.assertEqual(len(self.document.headings[0]), 3)
		self.assertEqual(self.document.headings[1].title, u'Überschrift 1')
		self.assertEqual(self.document.headings[1].start, 5)
		self.assertEqual(len(self.document.headings[1]), 4)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings), 4)
		self.assertEqual(d.headings[0].title, u'Test heading')
		self.assertEqual(d.headings[0].start, 2)
		self.assertEqual(d.headings[0]._orig_start, 2)
		self.assertEqual(len(d.headings[0]), 3)
		self.assertEqual(d.headings[1].title, u'Überschrift 1')
		self.assertEqual(d.headings[1].start, 5)
		self.assertEqual(len(d.headings[1]), 4)

	def test_write_add_heading_after_last_heading_toplevel(self):
		# add a heading after the last heading (top level heading)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.body = u'Text, text\nmore text'
		self.assertEqual(h.start, None)
		#self.document.headings += h
		self.document.headings.append(h)
		self.assertEqual(h.start, 21)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 4)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[-1].title, u'Test heading')
		self.assertEqual(self.document.headings[-1].start, 21)
		self.assertEqual(self.document.headings[-1]._orig_start, 21)
		self.assertEqual(len(self.document.headings[-1]), 3)
		self.assertEqual(self.document.headings[-2].title, u'Überschrift 3')
		self.assertEqual(self.document.headings[-2].start, 18)
		self.assertEqual(len(self.document.headings[-2]), 3)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings), 4)
		self.assertEqual(d.headings[-1].title, u'Test heading')
		self.assertEqual(d.headings[-1].start, 21)
		self.assertEqual(d.headings[-1]._orig_start, 21)
		self.assertEqual(len(d.headings[-1]), 3)
		self.assertEqual(d.headings[-2].title, u'Überschrift 3')
		self.assertEqual(d.headings[-2].start, 18)
		self.assertEqual(len(d.headings[-2]), 3)

	def test_write_add_heading_after_last_heading_subheading(self):
		# add a heading after the last heading (subheading)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.level = 2
		h.body = u'Text, text\nmore text'
		self.assertEqual(h.start, None)
		# TODO make it work with += operator so far it works with append and
		# extend so it seems that there is a problem in __iadd__ method in
		# UserList from collection in python3
		#self.document.headings[-1].children += h
		#self.document.headings[-1].children.extend([h])
		self.document.headings[-1].children.append(h)
		self.assertEqual(h.start, 21)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[-1]), 3)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[-1].children[-1].title, u'Test heading')
		self.assertEqual(self.document.headings[-1].children[-1].start, 21)
		self.assertEqual(self.document.headings[-1].children[-1]._orig_start, 21)
		self.assertEqual(len(self.document.headings[-1].children[-1]), 3)
		self.assertEqual(self.document.headings[-1].title, u'Überschrift 3')
		self.assertEqual(self.document.headings[-1].start, 18)
		self.assertEqual(len(self.document.headings[-1]), 3)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings), 3)
		self.assertEqual(len(d.headings[-1]), 3)
		self.assertEqual(d.headings[-1].children[-1].title, u'Test heading')
		self.assertEqual(d.headings[-1].children[-1].start, 21)
		self.assertEqual(d.headings[-1].children[-1]._orig_start, 21)
		self.assertEqual(len(d.headings[-1].children[-1]), 3)
		self.assertEqual(d.headings[-1].title, u'Überschrift 3')
		self.assertEqual(d.headings[-1].start, 18)
		self.assertEqual(len(d.headings[-1]), 3)

	def test_write_replace_one_heading(self):
		# replace subheadings by a list of newly created headings (one item)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.level = 3
		h.body = u'Text, text\nmore text\nanother text'
		self.assertEqual(h.start, None)
		self.document.headings[0].children[1].children[0] = h
		self.assertEqual(h.start, 13)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children[1].children), 2)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(self.document.headings[0].children[1].children[0].start, 13)
		self.assertEqual(self.document.headings[0].children[1].children[0]._orig_start, 13)
		self.assertEqual(len(self.document.headings[0].children[1].children[0]), 4)
		self.assertEqual(len(self.document.headings[0].children[1].children[0].children), 0)
		self.assertEqual(len(self.document.headings[0].children[1]), 3)
		self.assertEqual(len(self.document.headings[0].children[0].children), 0)
		self.assertEqual(len(self.document.headings[1].children), 0)
		self.assertEqual(self.document.headings[0].children[1].children[-1].title, u'Überschrift 1.2.1')
		self.assertEqual(self.document.headings[0].children[1].children[-1].start, 17)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings), 3)
		self.assertEqual(len(d.headings[0].children[1].children), 2)
		self.assertEqual(d.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(d.headings[0].children[1].children[0].start, 13)
		self.assertEqual(d.headings[0].children[1].children[0]._orig_start, 13)
		self.assertEqual(len(d.headings[0].children[1].children[0]), 4)
		self.assertEqual(len(d.headings[0].children[1].children[0].children), 0)
		self.assertEqual(len(d.headings[0].children[1]), 3)
		self.assertEqual(len(d.headings[0].children[0].children), 0)
		self.assertEqual(len(d.headings[1].children), 0)
		self.assertEqual(d.headings[0].children[1].children[-1].title, u'Überschrift 1.2.1')
		self.assertEqual(d.headings[0].children[1].children[-1].start, 17)

	def test_write_replace_multiple_headings_with_one_heading(self):
		# replace subheadings by a list of newly created headings (one item)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.level = 3
		h.body = u'Text, text\nmore text\nanother text'

		self.assertEqual(h.start, None)
		self.assertEqual(len(self.document.headings[0].children[1].children), 2)
		self.document.headings[0].children[1].children[:] = h
		self.assertEqual(h.start, 13)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].children[1].is_dirty, False)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children[1].children), 1)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].children[1].title, u'Überschrift 1.2')
		self.assertEqual(self.document.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(self.document.headings[0].children[1].children[0].start, 13)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings[0].children[1].children), 1)
		self.assertEqual(d.headings[0].children[1].title, u'Überschrift 1.2')
		self.assertEqual(d.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(d.headings[0].children[1].children[0].start, 13)

	def test_write_replace_multiple_headings_with_a_multiple_heading_structure(self):
		# replace subheadings by a list of newly created headings (multiple items)
		self.assertEqual(len(self.document.headings), 3)
		h = Heading()
		h.title = u'Test heading'
		h.level = 3
		h.body = u'Text, text\nmore text\nanother text'
		h1 = Heading()
		h1.title = u'another heading'
		h1.level = 4
		h1.body = u'This\nIs\nJust more\ntext'
		h.children.append(h1)
		h2 = Heading()
		h2.title = u'yet another heading'
		h2.level = 3
		h2.body = u'This\nis less text'

		self.assertEqual(h.start, None)
		self.document.headings[0].children[1].children[:] = (h, h2)
		self.assertEqual(h.start, 13)
		self.assertEqual(h1.start, 17)
		self.assertEqual(h2.start, 22)
		self.assertEqual(self.document.is_dirty, True)
		self.assertEqual(self.document.headings[0].children[1].is_dirty, False)
		self.assertEqual(len(self.document.headings), 3)
		self.assertEqual(len(self.document.headings[0].children[1].children), 2)
		self.assertEqual(len(self.document.headings[0].children[1].children[0].children), 1)
		self.assertEqual(len(self.document.headings[0].children[1].children[1].children), 0)

		self.assertEqual(self.document.write(), True)
		self.assertEqual(self.document.is_dirty, False)
		self.assertEqual(self.document.headings[0].children[1].title, u'Überschrift 1.2')
		self.assertEqual(self.document.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(self.document.headings[0].children[1].children[0].children[0].title, u'another heading')
		self.assertEqual(self.document.headings[0].children[1].children[1].title, u'yet another heading')
		self.assertEqual(self.document.headings[0].children[1].children[0].start, 13)
		self.assertEqual(self.document.headings[0].children[1].children[0].children[0].start, 17)
		self.assertEqual(self.document.headings[0].children[1].children[1].start, 22)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(d.headings[0].children[1].title, u'Überschrift 1.2')
		self.assertEqual(d.headings[0].children[1].children[0].title, u'Test heading')
		self.assertEqual(d.headings[0].children[1].children[0].children[0].title, u'another heading')
		self.assertEqual(d.headings[0].children[1].children[1].title, u'yet another heading')
		self.assertEqual(d.headings[0].children[1].children[0].start, 13)
		self.assertEqual(d.headings[0].children[1].children[0].children[0].start, 17)
		self.assertEqual(d.headings[0].children[1].children[1].start, 22)

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

		vim.current.buffer[:] = [ u_encode(i) for i in u"""
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		self.document = VimBuffer().init_dom()
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.parent, None)
		self.assertEqual(h.level, 2)
		self.assertEqual(h.title, u'Überschrift 1.2')
		self.assertEqual(len(h.children), 2)
		self.assertEqual(h.children[1].start, 7)
		self.assertEqual(h.children[1].children, [])
		self.assertEqual(h.children[1].next_sibling, None)
		self.assertEqual(h.children[1].end, 7)
		self.assertEqual(h.start, 1)
		self.assertEqual(h.end, 3)
		self.assertEqual(h.end_of_last_child, 7)

		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* Überschrift 2
* Überschrift 3""".split(u'\n') ]
		self.document = VimBuffer().init_dom()
		vim.current.window.cursor = (3, 0)
		h = self.document.current_heading()
		self.assertNotEqual(h, None)
		self.assertEqual(h.end, 2)
		self.assertEqual(h.end_of_last_child, 2)
		self.assertEqual(h.title, u'Überschrift 3')

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

class VimBufferTagsTestCase(unittest.TestCase):
	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'),
									   u_encode(u'DONE'), u_encode(u'|')],
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'0'),
				u_encode(u'&ts'): u_encode(u'8'),
				u_encode(u'exists("g:org_tag_column")'): u_encode(u'0'),
				u_encode(u'exists("b:org_tag_column")'): u_encode(u'0'),
				u_encode(u"v:count"): u_encode(u'0')}
		vim.current.buffer[:] = [ u_encode(i) for i in u"""#Meta information
#more meta information
* Überschrift 1     :testtag:
Text 1

Bla bla
** Überschrift 1.1 :multi:tags:
Text 2

Bla Bla bla
** Überschrift 1.2:notag:
Text 3

**** Überschrift 1.2.1.falsch :no tag:

Bla Bla bla bla
*** Überschrift 1.2.1 :no tag
*** Überschrift 1.2.2 no tag:
* Überschrift 2				  :more:tags:
* Überschrift 3	:lesser:tag:
  asdf sdf
* Überschrift 4 super long long long long long long long long extremely long title	:title:long:
* TODO Überschrift 5 super long long long long long long long long extremely long title	:title_with_todo:
* oneword :with:tags:
* :noword:with:tags:
* TODO :todo:with:tags:
""".split(u'\n') ]
		self.document = VimBuffer().init_dom()

	def test_tag_read_no_word_with_tags(self):
		self.assertEqual(len(self.document.headings[6].tags), 3)
		self.assertEqual(self.document.headings[6].tags[0], u'noword')
		self.assertEqual(self.document.headings[6].title, u'')
		self.assertEqual(self.document.headings[6].todo, None)

	def test_tag_read_one_word_with_tags(self):
		self.assertEqual(len(self.document.headings[5].tags), 2)
		self.assertEqual(self.document.headings[5].tags[0], u'with')
		self.assertEqual(self.document.headings[5].title, u'oneword')
		self.assertEqual(self.document.headings[5].todo, None)

	def test_tag_read_TODO_with_tags(self):
		self.assertEqual(len(self.document.headings[7].tags), 3)
		self.assertEqual(self.document.headings[7].tags[0], u'todo')
		self.assertEqual(self.document.headings[7].title, u'')
		self.assertEqual(self.document.headings[7].todo, u'TODO')

	def test_tag_read_one(self):
		self.assertEqual(len(self.document.headings[0].tags), 1)
		self.assertEqual(self.document.headings[0].tags[0], u'testtag')
		self.assertEqual(unicode(self.document.headings[0]), u'* Überschrift 1							    :testtag:')

	def test_tag_read_multiple(self):
		self.assertEqual(len(self.document.headings[0].children[0].tags), 2)
		self.assertEqual(self.document.headings[0].children[0].tags, [u'multi', 'tags'])
		self.assertEqual(unicode(self.document.headings[0].children[0]), u'** Überschrift 1.1						 :multi:tags:')

	def test_tag_no_tags(self):
		self.assertEqual(len(self.document.headings[0].children[1].children), 3)
		self.assertEqual(len(self.document.headings[0].children[1].tags), 0)
		self.assertEqual(len(self.document.headings[0].children[1].children[0].tags), 0)
		self.assertEqual(len(self.document.headings[0].children[1].children[1].tags), 0)
		self.assertEqual(len(self.document.headings[0].children[1].children[2].tags), 0)

	def test_tag_read_space_and_tab_separated(self):
		self.assertEqual(len(self.document.headings[1].children), 0)
		self.assertEqual(len(self.document.headings[1].tags), 2)
		self.assertEqual(self.document.headings[1].tags, [u'more', u'tags'])

	def test_tag_read_tab_separated(self):
		self.assertEqual(len(self.document.headings[2].children), 0)
		self.assertEqual(len(self.document.headings[2].tags), 2)
		self.assertEqual(self.document.headings[2].tags, [u'lesser', u'tag'])

	def test_tag_read_long_title(self):
		self.assertEqual(len(self.document.headings[3].children), 0)
		self.assertEqual(len(self.document.headings[3].tags), 2)
		self.assertEqual(self.document.headings[3].tags, [u'title', u'long'])
		self.assertEqual(unicode(self.document.headings[3]), u'* Überschrift 4 super long long long long long long long long extremely long title  :title:long:')

	def test_tag_read_long_title_plus_todo_state(self):
		self.assertEqual(len(self.document.headings[4].children), 0)
		self.assertEqual(len(self.document.headings[4].tags), 1)
		self.assertEqual(self.document.headings[4].level, 1)
		self.assertEqual(self.document.headings[4].todo, u'TODO')
		self.assertEqual(self.document.headings[4].title, u'Überschrift 5 super long long long long long long long long extremely long title')
		self.assertEqual(self.document.headings[4].tags, [u'title_with_todo'])
		self.assertEqual(unicode(self.document.headings[4]), u'* TODO Überschrift 5 super long long long long long long long long extremely long title  :title_with_todo:')

	def test_tag_del_tags(self):
		self.assertEqual(len(self.document.headings[0].tags), 1)
		del self.document.headings[0].tags
		self.assertEqual(len(self.document.headings[0].tags), 0)
		self.assertEqual(self.document.headings[0].is_dirty_heading, True)
		self.assertEqual(self.document.headings[0].is_dirty_body, False)
		self.assertEqual(unicode(self.document.headings[0]), u'* Überschrift 1')
		self.assertEqual(self.document.write(), True)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings[0].tags), 0)
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(d.headings[0]), u'* Überschrift 1')

	def test_tag_replace_one_tag(self):
		self.assertEqual(len(self.document.headings[0].tags), 1)
		self.document.headings[0].tags = [u'justonetag']
		self.assertEqual(len(self.document.headings[0].tags), 1)
		self.assertEqual(self.document.headings[0].is_dirty_heading, True)
		self.assertEqual(self.document.headings[0].is_dirty_body, False)
		self.assertEqual(unicode(self.document.headings[0]), u'* Überschrift 1							 :justonetag:')
		self.assertEqual(self.document.write(), True)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings[0].tags), 1)
		self.assertEqual(d.headings[0].tags, [u'justonetag'])
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(d.headings[0]), u'* Überschrift 1							 :justonetag:')

	def test_tag_replace_multiple_tags(self):
		self.assertEqual(len(self.document.headings[1].tags), 2)
		self.document.headings[1].tags = [u'justonetag', u'moretags', u'lesstags']
		self.assertEqual(len(self.document.headings[1].tags), 3)
		self.assertEqual(self.document.headings[1].is_dirty_heading, True)
		self.assertEqual(self.document.headings[1].is_dirty_body, False)
		self.assertEqual(unicode(self.document.headings[1]), u'* Überschrift 2				       :justonetag:moretags:lesstags:')
		self.assertEqual(self.document.write(), True)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(len(d.headings[1].tags), 3)
		self.assertEqual(d.headings[1].tags, [u'justonetag', u'moretags', u'lesstags'])
		self.assertEqual(d.headings[1].title, u'Überschrift 2')
		self.assertEqual(unicode(d.headings[1]), u'* Überschrift 2				       :justonetag:moretags:lesstags:')

class VimBufferTodoTestCase(unittest.TestCase):
	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'), \
						u_encode(u'DONß'), u_encode(u'DONÉ'), \
						u_encode(u'DÖNE'), u_encode(u'WAITING'), \
						u_encode(u'DONE'), u_encode(u'|')],
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'0'),
				u_encode(u'&ts'): u_encode(u'8'),
				u_encode(u'exists("g:org_tag_column")'): u_encode(u'0'),
				u_encode(u'exists("b:org_tag_column")'): u_encode(u'0'),
				u_encode(u"v:count"): u_encode(u'0')}
		vim.current.buffer[:] = [ u_encode(i) for i in u"""#Meta information
#more meta information
* TODO Überschrift 1     :testtag:
Text 1

Bla bla
** TODO NOTODO Überschrift 1.1 :multi:tags:
Text 2

Bla Bla bla
** NO-TODO Überschrift 1.2:notag:
Text 3

**** NOTODOÜberschrift 1.2.1.falsch :no tag:

Bla Bla bla bla
*** notodo Überschrift 1.2.1 :no tag
*** NOTODo Überschrift 1.2.2 no tag:
* WAITING Überschrift 2				  :more:tags:
* DONE Überschrift 3	:lesser:tag:
  asdf sdf
* DÖNE Überschrift 4
* DONß Überschrift 5
* DONÉ Überschrift 6
* DONé    Überschrift 7
""".split(u'\n') ]
		self.document = VimBuffer().init_dom()

	def test_no_space_after_upper_case_single_word_heading(self):
		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* TEST
** Text 1
*** Text 2
* Text 1
** Text 1
   some text that is
   no heading

""".split(u'\n') ]
		d = VimBuffer().init_dom()
		self.assertEqual(unicode(d.headings[0]), u'* TEST')

	def test_todo_read_TODO(self):
		self.assertEqual(self.document.headings[0].todo, u'TODO')
		self.assertEqual(self.document.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(self.document.headings[0]), u'* TODO Überschrift 1						    :testtag:')

	def test_todo_read_TODO_NOTODO(self):
		self.assertEqual(self.document.headings[0].children[0].todo, u'TODO')
		self.assertEqual(self.document.headings[0].children[0].title, u'NOTODO Überschrift 1.1')
		self.assertEqual(unicode(self.document.headings[0].children[0]), u'** TODO NOTODO Überschrift 1.1					 :multi:tags:')

	def test_todo_read_WAITING(self):
		self.assertEqual(self.document.headings[1].todo, u'WAITING')
		self.assertEqual(self.document.headings[1].title, u'Überschrift 2')
		self.assertEqual(unicode(self.document.headings[1]), u'* WAITING Überschrift 2						  :more:tags:')

	def test_todo_read_DONE(self):
		self.assertEqual(self.document.headings[2].todo, u'DONE')
		self.assertEqual(self.document.headings[2].title, u'Überschrift 3')
		self.assertEqual(unicode(self.document.headings[2]), u'* DONE Überschrift 3						 :lesser:tag:')

	def test_todo_read_special(self):
		self.assertEqual(self.document.headings[3].todo, u'DÖNE')
		self.assertEqual(self.document.headings[3].title, u'Überschrift 4')

		self.assertEqual(self.document.headings[4].todo, u'DONß')
		self.assertEqual(self.document.headings[4].title, u'Überschrift 5')

		self.assertEqual(self.document.headings[5].todo, u'DONÉ')
		self.assertEqual(self.document.headings[5].title, u'Überschrift 6')

		self.assertEqual(self.document.headings[6].todo, None)
		self.assertEqual(self.document.headings[6].title, u'DONé    Überschrift 7')

	def test_todo_del_todo(self):
		self.assertEqual(self.document.headings[0].todo, u'TODO')
		del self.document.headings[0].todo
		self.assertEqual(self.document.headings[0].is_dirty_body, False)
		self.assertEqual(self.document.headings[0].is_dirty_heading, True)
		self.assertEqual(self.document.headings[0].todo, None)
		self.assertEqual(self.document.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(self.document.headings[0]), u'* Überschrift 1							    :testtag:')
		self.assertEqual(self.document.write(), True)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(d.headings[0].todo, None)
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(d.headings[0]), u'* Überschrift 1							    :testtag:')

	def test_todo_write_todo_uppercase(self):
		self.assertEqual(self.document.headings[0].todo, u'TODO')
		self.document.headings[0].todo = u'DONE'
		self.assertEqual(self.document.headings[0].is_dirty_body, False)
		self.assertEqual(self.document.headings[0].is_dirty_heading, True)
		self.assertEqual(self.document.headings[0].todo, u'DONE')
		self.assertEqual(self.document.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(self.document.headings[0]), u'* DONE Überschrift 1						    :testtag:')
		self.assertEqual(self.document.write(), True)

		# sanity check
		d = VimBuffer().init_dom()
		self.assertEqual(d.headings[0].todo, u'DONE')
		self.assertEqual(d.headings[0].title, u'Überschrift 1')
		self.assertEqual(unicode(d.headings[0]), u'* DONE Überschrift 1						    :testtag:')

	def test_todo_set_illegal_todo(self):
		def set_todo(todo):
			self.document.headings[0].todo = todo
		self.assertEqual(self.document.headings[0].todo, u'TODO')
		self.assertRaises(ValueError, set_todo, u'DO NE')
		self.assertRaises(ValueError, set_todo, u'DO\tNE')
		self.assertRaises(ValueError, set_todo, u'D\nNE')
		self.assertRaises(ValueError, set_todo, u'DO\rNE')
		self.assertEqual(self.document.headings[0].todo, u'TODO')

def suite():
	return ( \
			unittest.TestLoader().loadTestsFromTestCase(VimBufferTestCase), \
			unittest.TestLoader().loadTestsFromTestCase(VimBufferTagsTestCase), \
			unittest.TestLoader().loadTestsFromTestCase(VimBufferTodoTestCase), \
			)
