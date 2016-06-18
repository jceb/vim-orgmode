# -*- coding: utf-8 -*-

"""
	vimbuffer
	~~~~~~~~~~

	VimBuffer and VimBufferContent are the interface between liborgmode and
	vim.

	VimBuffer extends the liborgmode.document.Document().
	Document() is just a general implementation for loading an org file. It
	has no interface to an actual file or vim buffer. This is the task of
	vimbuffer.VimBuffer(). It is the interfaces to vim. The main tasks for
	VimBuffer are to provide read and write access to a real vim buffer.

	VimBufferContent is a helper class for VimBuffer. Basically, it hides the
	details of encoding - everything read from or written to VimBufferContent
	is UTF-8.
"""

try:
	from collections import UserList
except:
	from UserList import UserList

import vim

from orgmode import settings
from orgmode.exceptions import BufferNotFound, BufferNotInSync
from orgmode.liborgmode.documents import Document, MultiPurposeList, Direction
from orgmode.liborgmode.headings import Heading

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *


class VimBuffer(Document):
	def __init__(self, bufnr=0):
		u"""
		:bufnr:		0: current buffer, every other number refers to another buffer
		"""
		Document.__init__(self)
		self._bufnr          = vim.current.buffer.number if bufnr == 0 else bufnr
		self._changedtick    = -1
		self._cached_heading = None
		if self._bufnr == vim.current.buffer.number:
			self._content = VimBufferContent(vim.current.buffer)
		else:
			_buffer = None
			for b in vim.buffers:
				if self._bufnr == b.number:
					_buffer = b
					break

			if not _buffer:
				raise BufferNotFound(u'Unable to locate buffer number #%d' % self._bufnr)
			self._content = VimBufferContent(_buffer)

		self.update_changedtick()
		self._orig_changedtick = self._changedtick

	@property
	def tabstop(self):
		return int(vim.eval(u_encode(u'&ts')))

	@property
	def tag_column(self):
		return int(settings.get(u'org_tag_column', u'77'))

	@property
	def is_insync(self):
		if self._changedtick == self._orig_changedtick:
			self.update_changedtick()
		return self._changedtick == self._orig_changedtick

	@property
	def bufnr(self):
		u"""
		:returns:	The buffer's number for the current document
		"""
		return self._bufnr

	@property
	def changedtick(self):
		u""" Number of changes in vimbuffer """
		return self._changedtick

	@changedtick.setter
	def changedtick(self, value):
		self._changedtick = value

	def get_todo_states(self, strip_access_key=True):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		:returns:	[([todo states], [done states]), ..]
		"""
		states = settings.get(u'org_todo_keywords', [])
		# TODO this function gets called too many times when change of state of
		# one todo is triggered, check with:
		# print(states)
		# this should be changed by saving todo states into some var and only
		# if new states are set hook should be called to register them again
		# into a property
		# TODO move this to documents.py, it is all tangled up like this, no
		# structure...
		if type(states) not in (list, tuple):
			return []

		def parse_states(s, stop=0):
			res = []
			if not s:
				return res
			if type(s[0]) in (unicode, str):
				r = []
				for i in s:
					_i = i
					if type(_i) == str:
						_i = u_decode(_i)
					if type(_i) == unicode and _i:
						if strip_access_key and u'(' in _i:
							_i = _i[:_i.index(u'(')]
							if _i:
								r.append(_i)
						else:
							r.append(_i)
				if not u'|' in r:
					if not stop:
						res.append((r[:-1], [r[-1]]))
					else:
						res = (r[:-1], [r[-1]])
				else:
					seperator_pos = r.index(u'|')
					if not stop:
						res.append((r[0:seperator_pos], r[seperator_pos + 1:]))
					else:
						res = (r[0:seperator_pos], r[seperator_pos + 1:])
			elif type(s) in (list, tuple) and not stop:
				for i in s:
					r = parse_states(i, stop=1)
					if r:
						res.append(r)
			return res

		return parse_states(states)

	def update_changedtick(self):
		if self.bufnr == vim.current.buffer.number:
			self._changedtick = int(vim.eval(u_encode(u'b:changedtick')))
		else:
			vim.command(u_encode(u'unlet! g:org_changedtick | let g:org_lz = &lz | let g:org_hidden = &hidden | set lz hidden'))
			# TODO is this likely to fail? maybe some error hangling should be added
			vim.command(u_encode(u'keepalt buffer %d | let g:org_changedtick = b:changedtick | buffer %d' % \
					(self.bufnr, vim.current.buffer.number)))
			vim.command(u_encode(u'let &lz = g:org_lz | let &hidden = g:org_hidden | unlet! g:org_lz g:org_hidden | redraw'))
			self._changedtick = int(vim.eval(u_encode(u'g:org_changedtick')))

	def write(self):
		u""" write the changes to the vim buffer

		:returns:	True if something was written, otherwise False
		"""
		if not self.is_dirty:
			return False

		self.update_changedtick()
		if not self.is_insync:
			raise BufferNotInSync(u'Buffer is not in sync with vim!')

		# write meta information
		if self.is_dirty_meta_information:
			meta_end = 0 if self._orig_meta_information_len is None else self._orig_meta_information_len
			self._content[:meta_end] = self.meta_information
			self._orig_meta_information_len = len(self.meta_information)

		# remove deleted headings
		already_deleted = []
		for h in sorted(self._deleted_headings, key=lambda x: x._orig_start, reverse=True):
			if h._orig_start is not None and h._orig_start not in already_deleted:
				# this is a heading that actually exists on the buffer and it
				# needs to be removed
				del self._content[h._orig_start:h._orig_start + h._orig_len]
				already_deleted.append(h._orig_start)
		del self._deleted_headings[:]
		del already_deleted

		# update changed headings and add new headings
		for h in self.all_headings():
			if h.is_dirty:
				vim.current.buffer.append("") # workaround for neovim bug
				if h._orig_start is not None:
					# this is a heading that existed before and was changed. It
					# needs to be replaced
					if h.is_dirty_heading:
						self._content[h.start:h.start + 1] = [unicode(h)]
					if h.is_dirty_body:
						self._content[h.start + 1:h.start + h._orig_len] = h.body
				else:
					# this is a new heading. It needs to be inserted
					self._content[h.start:h.start] = [unicode(h)] + h.body
				del vim.current.buffer[-1] # restore workaround for neovim bug
				h._dirty_heading = False
				h._dirty_body = False
			# for all headings the length and start offset needs to be updated
			h._orig_start = h.start
			h._orig_len = len(h)

		self._dirty_meta_information = False
		self._dirty_document = False

		self.update_changedtick()
		self._orig_changedtick = self._changedtick
		return True

	def write_heading(self, heading, including_children=True):
		""" WARNING: use this function only when you know what you are doing!
		This function writes a heading to the vim buffer. It offers performance
		advantages over the regular write() function. This advantage is
		combined with no sanity checks! Whenever you use this function, make
		sure the heading you are writing contains the right offsets
		(Heading._orig_start, Heading._orig_len).

		Usage example:
			# Retrieve a potentially dirty document
			d = ORGMODE.get_document(allow_dirty=True)
			# Don't rely on the DOM, retrieve the heading afresh
			h = d.find_heading(direction=Direction.FORWARD, position=100)
			# Update tags
			h.tags = ['tag1', 'tag2']
			# Write the heading
			d.write_heading(h)

		This function can't be used to delete a heading!

		:heading:				Write this heading with to the vim buffer
		:including_children:	Also include children in the update

		:returns				The written heading
		"""
		if including_children and heading.children:
			for child in heading.children[::-1]:
				self.write_heading(child, including_children)

		if heading.is_dirty:
			if heading._orig_start is not None:
				# this is a heading that existed before and was changed. It
				# needs to be replaced
				if heading.is_dirty_heading:
					self._content[heading._orig_start:heading._orig_start + 1] = [unicode(heading)]
				if heading.is_dirty_body:
					self._content[heading._orig_start + 1:heading._orig_start + heading._orig_len] = heading.body
			else:
				# this is a new heading. It needs to be inserted
				raise ValueError('Heading must contain the attribute _orig_start! %s' % heading)
			heading._dirty_heading = False
			heading._dirty_body = False
		# for all headings the length offset needs to be updated
		heading._orig_len = len(heading)

		return heading

	def write_checkbox(self, checkbox, including_children=True):
		if including_children and checkbox.children:
			for child in checkbox.children[::-1]:
				self.write_checkbox(child, including_children)

		if checkbox.is_dirty:
			if checkbox._orig_start is not None:
				# this is a heading that existed before and was changed. It
				# needs to be replaced
				# print "checkbox is dirty? " + str(checkbox.is_dirty_checkbox)
				# print checkbox
				if checkbox.is_dirty_checkbox:
					self._content[checkbox._orig_start:checkbox._orig_start + 1] = [unicode(checkbox)]
				if checkbox.is_dirty_body:
					self._content[checkbox._orig_start + 1:checkbox._orig_start + checkbox._orig_len] = checkbox.body
			else:
				# this is a new checkbox. It needs to be inserted
				raise ValueError('Checkbox must contain the attribute _orig_start! %s' % checkbox)
			checkbox._dirty_checkbox = False
			checkbox._dirty_body = False
		# for all headings the length offset needs to be updated
		checkbox._orig_len = len(checkbox)

		return checkbox

	def write_checkboxes(self, checkboxes):
		pass

	def previous_heading(self, position=None):
		u""" Find the next heading (search forward) and return the related object
		:returns:	Heading object or None
		"""
		h = self.current_heading(position=position)
		if h:
			return h.previous_heading

	def current_heading(self, position=None):
		u""" Find the current heading (search backward) and return the related object
		:returns:	Heading object or None
		"""
		if position is None:
			position = vim.current.window.cursor[0] - 1

		if not self.headings:
			return

		def binaryFindInDocument():
			hi = len(self.headings)
			lo = 0
			while lo < hi:
				mid = (lo+hi)//2
				h = self.headings[mid]
				if h.end_of_last_child < position:
					lo = mid + 1
				elif h.start > position:
					hi = mid
				else:
					return binaryFindHeading(h)

		def binaryFindHeading(heading):
			if not heading.children or heading.end >= position:
				return heading

			hi = len(heading.children)
			lo = 0
			while lo < hi:
				mid = (lo+hi)//2
				h = heading.children[mid]
				if h.end_of_last_child < position:
					lo = mid + 1
				elif h.start > position:
					hi = mid
				else:
					return binaryFindHeading(h)

		# look at the cache to find the heading
		h_tmp = self._cached_heading
		if h_tmp is not None:
			if h_tmp.end_of_last_child > position and \
					h_tmp.start < position:
				if h_tmp.end < position:
					self._cached_heading = binaryFindHeading(h_tmp)
				return self._cached_heading

		self._cached_heading = binaryFindInDocument()
		return self._cached_heading

	def next_heading(self, position=None):
		u""" Find the next heading (search forward) and return the related object
		:returns:	Heading object or None
		"""
		h = self.current_heading(position=position)
		if h:
			return h.next_heading

	def find_current_heading(self, position=None, heading=Heading):
		u""" Find the next heading backwards from the position of the cursor.
		The difference to the function current_heading is that the returned
		object is not built into the DOM. In case the DOM doesn't exist or is
		out of sync this function is much faster in fetching the current
		heading.

		:position:	The position to start the search from

		:heading:	The base class for the returned heading

		:returns:	Heading object or None
		"""
		return self.find_heading(vim.current.window.cursor[0] - 1 \
				if position is None else position, \
				direction=Direction.BACKWARD, heading=heading, \
				connect_with_document=False)


class VimBufferContent(MultiPurposeList):
	u""" Vim Buffer Content is a UTF-8 wrapper around a vim buffer. When
	retrieving or setting items in the buffer an automatic conversion is
	performed.

	This ensures UTF-8 usage on the side of liborgmode and the vim plugin
	vim-orgmode.
	"""

	def __init__(self, vimbuffer, on_change=None):
		MultiPurposeList.__init__(self, on_change=on_change)

		# replace data with vimbuffer to make operations change the actual
		# buffer
		self.data = vimbuffer

	def __contains__(self, item):
		i = item
		if type(i) is unicode:
			i = u_encode(item)
		return MultiPurposeList.__contains__(self, i)

	def __getitem__(self, i):
		if isinstance(i, slice):
			return [u_decode(item) if type(item) is str else item \
					for item in MultiPurposeList.__getitem__(self, i)]
		else:
			item = MultiPurposeList.__getitem__(self, i)
			if type(item) is str:
				return u_decode(item)
			return item

	def __setitem__(self, i, item):
		if isinstance(i, slice):
			o = []
			o_tmp = item
			if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
				o_tmp = list(o_tmp)
			for item in o_tmp:
				if type(item) == unicode:
					o.append(u_encode(item))
				else:
					o.append(item)
			MultiPurposeList.__setitem__(self, i, o)
		else:
			_i = item
			if type(_i) is unicode:
				_i = u_encode(item)

			# TODO: fix this bug properly, it is really strange that it fails on
			# python3 without it. Problem is that when _i = ['* '] it fails in
			# UserList.__setitem__() but if it is changed in debuggr in __setitem__
			# like item[0] = '* ' it works, hence this is some quirk with unicode
			# stuff but very likely vim 7.4 BUG too.
			if isinstance(_i, UserList) and sys.version_info > (3, ):
				_i = [s.encode('utf8').decode('utf8') for s in _i]

			MultiPurposeList.__setitem__(self, i, _i)

	def __add__(self, other):
		raise NotImplementedError()
		# TODO: implement me
		if isinstance(other, UserList):
			return self.__class__(self.data + other.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(self.data + other)
		else:
			return self.__class__(self.data + list(other))

	def __radd__(self, other):
		raise NotImplementedError()
		# TODO: implement me
		if isinstance(other, UserList):
			return self.__class__(other.data + self.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(other + self.data)
		else:
			return self.__class__(list(other) + self.data)

	def __iadd__(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) is unicode:
				o.append(u_encode(i))
			else:
				o.append(i)

		return MultiPurposeList.__iadd__(self, o)

	def append(self, item):
		i = item
		if type(item) is str:
			i = u_encode(item)
		MultiPurposeList.append(self, i)

	def insert(self, i, item):
		_i = item
		if type(_i) is str:
			_i = u_encode(item)
		MultiPurposeList.insert(self, i, _i)

	def index(self, item, *args):
		i = item
		if type(i) is unicode:
			i = u_encode(item)
		MultiPurposeList.index(self, i, *args)

	def pop(self, i=-1):
		return u_decode(MultiPurposeList.pop(self, i))

	def extend(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple) and not isinstance(o_tmp, UserList):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) is unicode:
				o.append(u_encode(i))
			else:
				o.append(i)
		MultiPurposeList.extend(self, o)


# vim: set noexpandtab:
