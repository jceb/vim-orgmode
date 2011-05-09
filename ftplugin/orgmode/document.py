# -*- coding: utf-8 -*-

from exceptions import BufferNotFound
from liborgmode import Document, Heading, MultiPurposeList
import vim

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
		if type(i) == unicode:
			i = item.encode(u'utf-8')
		return MultiPurposeList.__contains__(self, i)

	def __getitem__(self, i):
		item = MultiPurposeList.__getitem__(self, i)
		if type(item) == str:
			return item.decode(u'utf-8')
		return item

	def __getslice__(self, i, j):
		return [item.decode(u'utf-8') if type(item) == str else item for item in MultiPurposeList.__getslice__(self, i, j)]

	def __setitem__(self, i, item):
		_i = item
		if type(_i) == unicode:
			_i = item.encode(u'utf-8')

		MultiPurposeList.__setitem__(self, i, _i)

	def __setslice__(self, i, j, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple, self.__class__):
			o_tmp = list(o_tmp)
		for item in o_tmp:
			if type(item) == unicode:
				o.append(item.encode(u'utf-8'))
			else:
				o.append(item)
		MultiPurposeList.__setslice__(self, i, j, o)

	def __add__(self, other):
		# TODO: implement me
		if isinstance(other, MultiPurposeList):
			return self.__class__(self.data + other.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(self.data + other)
		else:
			return self.__class__(self.data + list(other))

	def __radd__(self, other):
		# TODO: implement me
		if isinstance(other, MultiPurposeList):
			return self.__class__(other.data + self.data)
		elif isinstance(other, type(self.data)):
			return self.__class__(other + self.data)
		else:
			return self.__class__(list(other) + self.data)

	def __iadd__(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple, self.__class__):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) == unicode:
				o.append(i.encode(u'utf-8'))
			else:
				o.append(i)

		return MultiPurposeList.__iadd__(self, o)

	def append(self, item):
		i = item
		if type(item) == str:
			i = item.encode(u'utf-8')
		MultiPurposeList.append(self, i)

	def insert(self, i, item):
		_i = item
		if type(_i) == str:
			_i = item.encode(u'utf-8')
		MultiPurposeList.insert(self, i, _i)

	def index(self, item, *args):
		i = item
		if type(i) == unicode:
			i = item.encode(u'utf-8')
		MultiPurposeList.index(self, i, *args)

	def pop(self, i=-1):
		return MultiPurposeList.pop(self, i).decode(u'utf-8')

	def extend(self, other):
		o = []
		o_tmp = other
		if type(o_tmp) not in (list, tuple, self.__class__):
			o_tmp = list(o_tmp)
		for i in o_tmp:
			if type(i) == unicode:
				o.append(i.encode(u'utf-8'))
			else:
				o.append(i)
		MultiPurposeList.extend(self, o)

class VimBuffer(Document):
	def __init__(self, bufnr=0):
		u"""
		:bufnr:		0: current buffer, every other number refers to another buffer
		"""
		Document.__init__(self)
		self._bufnr = bufnr

	@property
	def bufnr(self):
		u"""
		:returns:	The buffer's number for the current document
		"""
		return self._bufnr

	def load(self, heading=Heading):
		if self._bufnr == 0:
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
		return Document.load(self, heading=Heading)

	def write(self):
		u""" write the changes to the vim buffer

		:returns:	True if something was written, otherwise False
	    """
		if not self.is_dirty:
			return False

		# write meta information
		if self.is_dirty_meta_information:
			meta_end = 0 if self._orig_meta_information_len == None else self._orig_meta_information_len
			self._content[:meta_end] = self._meta_information
			self._orig_meta_information_len = len(self._meta_information)
			self._dirty_meta_information = False

		# remove deleted headings
		already_deleted = []
		for h in sorted(self._deleted_headings, cmp=lambda x, y: cmp(x._orig_start, y._orig_start), reverse=True):
			if h._orig_start != None and h not in already_deleted:
				# this is a heading that actually exists on the buffer and it
				# needs to be removed
				del self._content[h._orig_start:h._orig_start + h._orig_len]
				already_deleted.append(h)
		del self._deleted_headings[:]
		del already_deleted

		# update changed headings and add new headings
		for h in self.all_headings():
			if h.is_dirty:
				if h._orig_start != None:
					# this is a heading that existed before and was changed. It
					# needs to be replaced
					if h.is_dirty_heading:
						self._content[h.start:h.start + 1] = [unicode(h)]
					if h.is_dirty_body:
						self._content[h.start + 1:h.start + h._orig_len] = h.body
				else:
					# this is a new heading. It needs to be inserted
					self._content[h.start:h.start] = [unicode(h)] + h.body
				h._dirty_heading = False
				h._dirty_body = False
			# for all headings the length and start offset needs to be updated
			h._orig_start = h.start
			h._orig_len = len(h)

		self._dirty = False
		return True

	def previous_heading(self):
		u""" Find the next heading (search forward) and return the related object
		:returns:	 Heading object or None
		"""
		h = self.current_heading()
		if h:
			return h.previous_heading

	def current_heading(self):
		u""" Find the current heading (search backward) and return the related object
		:returns:	Heading object or None
		"""
		position = vim.current.window.cursor[0] - 1
		for h in self.all_headings():
			if h.start <= position and h.end >= position:
				return h

	def next_heading(self):
		u""" Find the next heading (search forward) and return the related object
		:returns:	 Heading object or None
		"""
		h = self.current_heading()
		if h:
			return h.next_heading
