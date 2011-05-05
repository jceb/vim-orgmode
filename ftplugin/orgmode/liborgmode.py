# -*- coding: utf-8 -*-

import re
from UserList import UserList

from orgmode import settings

DIRECTION_FORWARD  = True
DIRECTION_BACKWARD = False

class MultiPurposeList(UserList):
	""" A Multi Purpose List is a list that calls a user defined hook on
	change. The impelementation is very basic - the hook is called without any
	parameters. Otherwise the Multi Purpose List can be used like any other
	list.

	The member element "data" can be used to fill the list without causing the
	list to be marked dirty. This should only be used during initialization!
	"""

	def __init__(self, initlist=None, on_change=None):
		UserList.__init__(self, initlist)
		self._on_change = on_change

	def _changed(self):
		"""
		Call hook
		"""
		if callable(self._on_change):
			self._on_change()

	def __setitem__(self, i, item):
		UserList.__setitem__(self, i, item)
		self._changed()

	def __delitem__(self, i):
		UserList.__delitem__(self, i)
		self._changed()

	def __setslice__(self, i, j, other):
		UserList.__setslice__(self, i, j, other)
		self._changed()

	def __delslice__(self, i, j):
		UserList.__delslice__(self, i, j)
		self._changed()

	def __iadd__(self, other):
		res = UserList.__iadd__(self, other)
		self._changed()
		return res

	def __imul__(self, n):
		res = UserList.__imul__(self, n)
		self._changed()
		return res

	def append(self, item):
		UserList.append(self, item)
		self._changed()

	def insert(self, i, item):
		self.__setitem__(i, item)

	def pop(self, i=-1):
		item = self[i]
		del self[i]
		return item

	def remove(self, item):
		self.__delitem__(self.data.index(item))

	def reverse(self):
		UserList.reverse(self)
		self._changed()

	def sort(self, *args, **kwds):
		UserList.sort(self, *args, **kwds)
		self._changed()

	def extend(self, other):
		UserList.extend(self, other)
		self._changed()

class HeadingList(MultiPurposeList):
	"""
	A Heading List just contains headings. It's used for documents to store top
	level headings and for headings to store subheadings.

	A Heading List must be linked to a Document or Heading!

	See documenatation of MultiPurposeList for more information.
	"""
	def __init__(self, obj, initlist=None):
		# it's not necessary to register a on_change hook because the heading
		# list will itself take care of marking headings dirty or adding
		# headings to the deleted headings list
		MultiPurposeList.__init__(self)

		self._obj = obj
		if not (isinstance(obj, Document) or self.__class__.is_heading(obj)):
			raise ValueError('A Heading List must be linked to a Document or Heading object!')

		# initialization must be done here, because
		# self._document is not initialized when the
		# constructor of MultiPurposeList is called
		if initlist:
			self.extend(initlist)

	@classmethod
	def is_heading(cls, obj):
		return isinstance(obj, Heading)

	def _get_document(self):
		if self.__class__.is_heading(self._obj):
			return self._obj._document
		return self._obj

	def _add_to_deleted_headings(self, item):
		"""
		Serialize headings so that all subheadings are also marked for deletion
		"""
		if not self._get_document():
			# heading has not been associated yet
			return

		if type(item) in (HeadingList, tuple, list):
			for i in item:
				self._add_to_deleted_headings(i.children)
		else:
			self._get_document()._deleted_headings.append(item)
			self._add_to_deleted_headings(item.children)

	def _associate_heading(self, item, children=False):
		# TODO this method should be externalized and moved to the Heading class
		if type(item) in (HeadingList, tuple, list):
			for i in item:
				self._associate_heading(i, children=children)
		else:
			item.set_dirty()
			item._orig_start = None
			item._orig_len = None
			d = self._get_document()
			if item._document != d:
				item._document = d
			if not children:
				if d == self._obj:
					# self._obj is a Document
					item._parent = None
				elif item._parent != self._obj:
					# self._obj is a Heading
					item._parent = self._obj

			self._associate_heading(item.children, children=True)

	def __setitem__(self, i, item):
		if not self.__class__.is_heading(item):
			raise ValueError('Item is not a heading!')
		if item in self.data:
			raise ValueError('Heading is already part of this list!')
		self._add_to_deleted_headings(item)

		self._associate_heading(item)
		MultiPurposeList.__setitem__(self, i, item)

	def __setslice__(self, i, j, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError('List contains items that are not a heading!')
		self._associate_heading(o)
		i = max(i, 0); j = max(j, 0)
		self._add_to_deleted_headings(self.data[i:j])
		MultiPurposeList.__setslice__(self, i, j, o)

	def __delitem__(self, i):
		self._add_to_deleted_headings(self.data[i])
		MultiPurposeList.__delitem__(self, i)

	def __delslice__(self, i, j):
		i = max(i, 0); j = max(j, 0)
		self._add_to_deleted_headings(self.data[i:j])
		MultiPurposeList.__delslice__(self, i, j)

	def __iadd__(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError('List contains items that are not a heading!')
		self._associate_heading(o)
		return MultiPurposeList.__iadd__(self, o)

	def __imul__(self, n):
		# TODO das müsste eigentlich ein klonen von objekten zur Folge haben
		return MultiPurposeList.__imul__(self, n)

	def append(self, item):
		if not self.__class__.is_heading(item):
			raise ValueError('Item is not a heading!')
		if item in self.data:
			raise ValueError('Heading is already part of this list!')
		self._associate_heading(item)
		MultiPurposeList.append(self, item)

	def insert(self, i, item):
		self.__setitem__(i, item)

	def pop(self, i=-1):
		item = self[i]
		self._add_to_deleted_headings(item)
		del self[i]
		return item

	def remove(self, item):
		MultiPurposeList.remove(self, item)

	def reverse(self):
		for i in self:
			i.set_dirty()
		MultiPurposeList.reverse(self)

	def sort(self, *args, **kwds):
		for i in self:
			i.set_dirty()
		MultiPurposeList.sort(*args, **kwds)

	def extend(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError('List contains items that are not a heading!')
		self._associate_heading(o)
		MultiPurposeList.extend(self, o)

REGEX_HEADING = re.compile('^(?P<level>\*+)( (?P<todo>[A-Z]+))?( (?P<title>.*?))?\s*(?P<tags>:[a-zA-Z:]+:)?$')

class Heading(object):
	""" Structural heading object """

	def __init__(self, document=None, data=None, orig_start=None):
		"""
		:document:	The document object this heading belongs to
		:data:		When creating a new heading from a file or buffer this is a
					list of lines/data belonging to the heading. The first line
					must contain the heading!
		:orig_start:	The original start of the heading in case it was read
						from a document.
		"""
		object.__init__(self)

		self._document      = document
		self._parent        = None
		self._dirty_heading = False
		self._dirty_body    = False
		self._orig_len      = len(data) if data else 0
		self._orig_start    = orig_start
		self._body          = MultiPurposeList(initlist = data[1:] if data else [], on_change=self.set_dirty_body)
		self._level, self._title, self._tags, self._todo = self.__class__.parse_title(data[0] if data else '')

		self._children  = HeadingList(self)

	def __str__(self):
		# TODO this must return a properly formatted heading!!!!
		return ' '.join(('*'*self.level, self.title))

	def __len__(self):
		return 1 + len(self.body)

	@classmethod
	def parse_title(cls, heading_line):
		m = REGEX_HEADING.match(heading_line)
		if m:
			r = m.groupdict()
			title = r['title'] if r['title'] else ''
			tags = r['tags'] if r['tags'] else []
			return (len(r['level']), title, tags, r['todo'])
		return (1, '', [], None)

	@classmethod
	def identify_heading(cls, line):
		""" Test if a certain line is a heading or not.

		:line: the line to check

		:returns: level
		"""
		level = 0
		if not line:
			return None
		for i in xrange(0, len(line)):
			if line[i] == '*':
				level += 1
				if len(line) > (i + 1) and line[i+1] in ('\t', ' '):
					return level
			else:
				return None

	def children():
		""" Subheadings of the current heading """
		def fget(self):
			return self._children
		def fset(self, value):
			self._children[:] = value
		return locals()
	children = property(**children())

	def body():
		""" Holds the content belonging to the heading """
		def fget(self):
			return self._body

		def fset(self, value):
			if type(value) in (list, tuple):
				self._body[:] = value
			elif type(value) in (unicode, str):
				self._body[:] = value.split('\n')
			else:
				self._body[:] = list(str(value))
		return locals()
	body = property(**body())

	@property
	def document(self):
		""" Read only access to the document. If you want to change the
		document, just assign the heading to another document """
		return self._document

	def set_dirty(self):
		""" Mark the heading dirty so that it will be rewritten when saving the
		document """
		self._dirty_heading = True
		self._dirty_body = True

	def set_dirty_heading(self):
		""" Mark the heading dirty so that it will be rewritten when saving the
		document """
		self._dirty_heading = True

	def set_dirty_body(self):
		""" Mark the heading dirty so that it will be rewritten when saving the
		document """
		self._dirty_body = True

	@property
	def is_dirty(self):
		""" Return True if the heading is marked dirty """
		return self._dirty_heading or self._dirty_body

	@property
	def is_dirty_heading(self):
		""" Return True if the heading is marked dirty """
		return self._dirty_heading

	@property
	def is_dirty_body(self):
		""" Return True if the heading is marked dirty """
		return self._dirty_body

	def title():
		""" Access to the title of the heading """
		def fget(self):
			return self._title
		def fset(self, value):
			if type(value) in (unicode, str):
				self._title = value
			else:
				self._title = str(value)
			self.set_dirty_heading()
		return locals()
	title = property(**title())

	def level():
		""" Access to the heading level """
		def fget(self):
			return self._level
		def fset(self, value):
			self._level = int(value)
			self.set_dirty_heading()
		return locals()
	level = property(**level())

	@property
	def start(self):
		""" Access to the starting line of the heading """
		if not self.document:
			return

		def compute_start(h):
			if h:
				return len(h) + compute_start(h.previous_heading)
			return len(self.document.meta_information) if self.document.meta_information else 0
		return compute_start(self.previous_heading)

	@property
	def start_vim(self):
		if self.start != None:
			return self.start + 1

	@property
	def end(self):
		""" Access to the ending line of the heading """
		if self.start != None:
			return self.start + len(self.body)

	@property
	def end_vim(self):
		if self.end != None:
			return self.end + 1

	@property
	def end_of_last_child(self):
		""" Access to end of the last child """
		if self.children:
			child = self.children[-1]
			while child.children:
				child = child.children[-1]
			return child.end
		return self.end

	@property
	def end_of_last_child_vim(self):
		return self.end_of_last_child + 1

	@property
	def first_child(self):
		""" Access to the first child heading or None if no children exist """
		if self.children:
			return self.children[0]

	@property
	def last_child(self):
		""" Access to the last child heading or None if no children exist """
		if self.children:
			return self.children[-1]

	@property
	def parent(self):
		""" Access to the parent heading """
		return self._parent

	@property
	def number_of_parents(self):
		""" Access to the number of parent headings before reaching the root
		document """
		def count_parents(h):
			if h.parent:
				return 1 + count_parents(h.parent)
			else:
				return 0
		return count_parents(self)

	@property
	def previous_sibling(self):
		""" Access to the previous heading that's a sibling of the current one
		"""
		if self.parent and self in self.parent.children:
			idx = self.parent.children.index(self)
			if idx > 0:
				return self.parent.children[idx - 1]
		elif not self.parent and self.document and self in self.document.headings:
			idx = self.document.headings.index(self)
			if idx > 0:
				return self.document.headings[idx - 1]

	@property
	def next_sibling(self):
		""" Access to the next heading that's a sibling of the current one """
		if self.parent and self in self.parent.children:
			idx = self.parent.children.index(self)
			if len(self.parent.children) > idx + 1:
				return self.parent.children[idx + 1]
		elif not self.parent and self.document and self in self.document.headings:
			idx = self.document.headings.index(self)
			if len(self.document.headings) > idx + 1:
				return self.document.headings[idx + 1]

	@property
	def previous_heading(self):
		""" Serialized access to the previous heading """
		if self.previous_sibling:
			h = self.previous_sibling
			while h.children:
				h = h.children[-1]
			return h
		elif self.parent:
			return self.parent

	@property
	def next_heading(self):
		""" Serialized access to the next heading """
		if self.children:
			return self.children[0]
		elif self.next_sibling:
			return self.next_sibling
		else:
			h = self.parent
			while h:
				if h.next_sibling:
					return h.next_sibling
				else:
					h = h.parent
	def tags():
		""" Tags """
		def fget(self):
			if self._tags == None:
				text = self.text.split()
				if not text or len(text[-1]) <= 2 or text[-1][0] != ':' or text[-1][-1] != ':':
					self._tags = []
				else:
					self._tags = [ x for x in text[-1].split(':') if x ]
			return self._tags

		def fset(self, value):
			"""
			:value:	list of tags, the empty list deletes all tags
			"""
			# find beginning of tags
			text = self.text.decode('utf-8')
			idx = text.rfind(' ')
			idx2 = text.rfind('\t')
			idx = idx if idx > idx2 else idx2

			if not value:
				if self.tags:
					# remove tags
					vim.current.buffer[self.start] = '%s %s' % ('*'*self.level, text[:idx].strip().encode('utf-8'))
			else:
				if self.tags:
					text = text[:idx]
				text = text.strip()

				tabs = 0
				spaces = 2
				tags = ':%s:' % (':'.join(value))

				tag_column = int(settings.get('org_tags_column', '77'))

				len_heading = self.level + 1 + len(text)
				if len_heading + spaces + len(tags) < tag_column:
					ts = int(vim.eval('&ts'))
					tmp_spaces =  ts - divmod(len_heading, ts)[1]

					if len_heading + tmp_spaces + len(tags) < tag_column:
						tabs, spaces = divmod(tag_column - (len_heading + tmp_spaces + len(tags)), ts)

						if tmp_spaces:
							tabs += 1
					else:
						spaces = tag_column - (len_heading + len(tags))

				# add tags
				vim.current.buffer[self.start] = '%s %s%s%s%s' % ('*'*self.level, text.encode('utf-8'), '\t'*tabs, ' '*spaces, tags)

			self._tags = value
		return locals()
	tags = property(**tags())

	def todo():
		"""Set and get todo state """
		def fget(self):
			# extract todo state from heading
			return self._todo
		def fset(self, value):
			# update todo state
			self._todo = value
		return locals()
	todo = property(**todo())

class Document(object):
	""" Representation of a whole org-mode document """

	def __init__(self):
		"""
		Don't call this constructor directly but use one of the concrete
		implementations.
		"""
		object.__init__(self)

		# is a list - only the Document methods should work with this list!
		self._content                   = None
		self._dirty_meta_information     = False
		self._meta_information          = MultiPurposeList(on_change = self.set_dirty_meta_information)
		self._orig_meta_information_len = None
		self._headings                  = HeadingList(self)
		self._deleted_headings          = []

	def _init_dom(self):
		""" Initialize all headings in document - build DOM

		:returns: None
	    """
		def init_heading(heading):
			"""
			:returns: the initialized heading
			"""
			start = heading.end + 1
			while True:
				new_heading = self.find_heading(start)

				# * Heading 1 <- heading
				# * Heading 1 <- sibling
				# or
				# * Heading 2 <- heading
				# * Heading 1 <- parent's sibling
				if not new_heading or \
						new_heading.level <= heading.level:
					break

				# * Heading 1 <- heading
				#  * Heading 2 <- first child
				#  * Heading 2 <- another child
				new_heading._parent = heading
				heading.children.data.append(new_heading)
				# the start and end computation is only
				# possible when the new heading was properly
				# added to the document structure
				init_heading(new_heading)
				if new_heading.children:
					# skip children
					start = new_heading.end_of_last_child + 1
				else:
					start = new_heading.end + 1

			return heading

		h = self.find_heading()
		# initialize meta information
		if h:
			self._meta_information.data.extend(self._content[:h._orig_start])
		else:
			self._meta_information.data.extend(self._content[:])
		self._orig_meta_information_len = len(self.meta_information)

		# initialize dom tree
		while h:
			self.headings.data.append(h)
			init_heading(h)
			h = self.find_heading(h.end_of_last_child + 1)

	def meta_information():
		"""
		Meta information is text that precedes all headings in an org-mode
		document. It might contain additional information about the document,
		e.g. author
		 """
		def fget(self):
			return self._meta_information

		def fset(self, value):
			if self._orig_meta_information_len == None:
				self._orig_meta_information_len = len(self.meta_information)
			if type(value) in (list, tuple):
				self._meta_information[:] = value
			elif type(value) in (unicode, str):
				self._meta_information[:] = value.split('\n')
			self.set_dirty_meta_information()
		return locals()
	meta_information = property(**meta_information())

	def headings():
		""" List of top level headings """
		def fget(self):
			return self._headings
		def fset(self, value):
			self._headings[:] = value
		return locals()
	headings = property(**headings())

	def write(self):
		""" write the document

		:returns:	True if something was written, otherwise False
		"""
		raise NotImplementedError('Abstract method, please use concrete impelementation!')

	def set_dirty_meta_information(self):
		self._dirty_meta_information = True

	@property
	def is_dirty(self):
		"""
		Return information about unsaved changes for the document and all
		related headings.

		:returns:	 Return True if document contains unsaved changes.
		"""
		if self.is_dirty_meta_information:
			return True

		if self._deleted_headings:
			return True

		if not self.headings:
			return False

		for h in self.headings:
			if h.is_dirty:
				return True
			for child in h.children:
				if child.is_dirty:
					return True

		return False

	@property
	def is_dirty_meta_information(self):
		return self._dirty_meta_information

	def all_headings(self):
		""" Iterate over all headings of the current document in serialized
		order

		:returns:	Returns an iterator object which returns all headings of
					the current file in serialized order
		"""
		if not self.headings:
			raise StopIteration()

		h = self.headings[0]
		while h:
			yield h
			h = h.next_heading
		raise StopIteration()

	def find_heading(self, position=0, direction=DIRECTION_FORWARD, heading=Heading):
		""" Find heading in the given direction

		:postition:	starting line, counting from 0 (in vim you start counting from 1, don't forget)
		:direction:	downwards == DIRECTION_FORWARD, upwards == DIRECTION_BACKWARD
		:heading:	Heading class from which new heading objects will be instanciated

		:returns:	New heading object or None
		"""
		len_cb = len(self._content)

		if position < 0 or position > len_cb:
			return

		tmp_line = position
		start = None
		end = None

		# Search heading upwards
		if direction == DIRECTION_FORWARD:
			while tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) != None:
					if start == None:
						start = tmp_line
					elif end == None:
						end = tmp_line - 1
					if None not in (start, end):
						break
				tmp_line += 1
		else:
			while tmp_line >= 0 and tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) != None:
					if start == None:
						start = tmp_line
					elif end == None:
						end = tmp_line - 1
					if None not in (start, end):
						break
				tmp_line -= 1 if start == None else -1

		if start != None and end == None:
			end = len_cb - 1
		if None not in (start, end):
			return heading(self, data=self._content[start:end + 1], orig_start=start)
