# -*- coding: utf-8 -*-

"""
	documents
	~~~~~~~~~

	TODO: explain this :)
"""

from UserList import UserList

from orgmode.liborgmode.base import MultiPurposeList, flatten_list, Direction
from orgmode.liborgmode.headings import Heading, HeadingList


class Document(object):
	u"""
	Representation of a whole org-mode document.

	A Document consists basically of headings (see Headings) and some metadata.

	TODO: explain the 'dirty' mechanism
	"""

	def __init__(self):
		u"""
		Don't call this constructor directly but use one of the concrete
		implementations.

		TODO: what are the concrete implementatiions?
		"""
		object.__init__(self)

		# is a list - only the Document methods should work with this list!
		self._content = None
		self._dirty_meta_information = False
		self._dirty_document = False
		self._meta_information = MultiPurposeList(on_change = self.set_dirty_meta_information)
		self._orig_meta_information_len = None
		self._headings = HeadingList(obj=self)
		self._deleted_headings = []

		# settings needed to align tags properly
		self._tabstop = 8
		self._tag_column = 77

		self.todo_states = [u'TODO', u'DONE']

	def __unicode__(self):
		if self.meta_information is None:
			return '\n'.join(self.all_headings())
		return '\n'.join(self.meta_information) + '\n' + '\n'.join(['\n'.join([unicode(i)] + i.body) for i in self.all_headings()])

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def get_all_todo_states(self):
		u""" Convenience function that returns all todo and done states and
		sequences in one big list.

		:returns:	[all todo/done states]
		"""
		return flatten_list(self.get_todo_states())

	def get_todo_states(self):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		:returns:	[([todo states], [done states]), ..]
		"""
		return self.todo_states

	def tabstop():
		u""" Tabstop for this document """
		def fget(self):
			return self._tabstop

		def fset(self, value):
			self._tabstop = value

		return locals()
	tabstop = property(**tabstop())

	def tag_column():
		u""" The column all tags are right-aligned to """
		def fget(self):
			return self._tag_column

		def fset(self, value):
			self._tag_column = value

		return locals()
	tag_column = property(**tag_column())

	def init_dom(self, heading=Heading):
		u""" Initialize all headings in document - build DOM. This method
		should be call prior to accessing the document.

		:returns:	self
		"""
		def init_heading(_h):
			u"""
			:returns	the initialized heading
			"""
			start = _h.end + 1
			prev_heading = None
			while True:
				new_heading = self.find_heading(start, heading=heading)

				# * Heading 1 <- heading
				# * Heading 1 <- sibling
				# or
				# * Heading 2 <- heading
				# * Heading 1 <- parent's sibling
				if not new_heading or \
						new_heading.level <= _h.level:
					break

				# * Heading 1 <- heading
				#  * Heading 2 <- first child
				#  * Heading 2 <- another child
				new_heading._parent = _h
				if prev_heading:
					prev_heading._next_sibling = new_heading
					new_heading._previous_sibling = prev_heading
				_h.children.data.append(new_heading)
				# the start and end computation is only
				# possible when the new heading was properly
				# added to the document structure
				init_heading(new_heading)
				if new_heading.children:
					# skip children
					start = new_heading.end_of_last_child + 1
				else:
					start = new_heading.end + 1
				prev_heading = new_heading

			return _h

		h = self.find_heading(heading=heading)
		# initialize meta information
		if h:
			self._meta_information.data.extend(self._content[:h._orig_start])
		else:
			self._meta_information.data.extend(self._content[:])
		self._orig_meta_information_len = len(self.meta_information)

		# initialize dom tree
		prev_h = None
		while h:
			if prev_h:
				prev_h._next_sibling = h
				h._previous_sibling = prev_h
			self.headings.data.append(h)
			init_heading(h)
			prev_h = h
			h = self.find_heading(h.end_of_last_child + 1, heading=heading)

		return self

	def meta_information():
		u"""
		Meta information is text that precedes all headings in an org-mode
		document. It might contain additional information about the document,
		e.g. author
		"""
		def fget(self):
			return self._meta_information

		def fset(self, value):
			if self._orig_meta_information_len is None:
				self._orig_meta_information_len = len(self.meta_information)
			if type(value) in (list, tuple) or isinstance(value, UserList):
				self._meta_information[:] = flatten_list(value)
			elif type(value) in (str, ):
				self._meta_information[:] = value.decode(u'utf-8').split(u'\n')
			elif type(value) in (unicode, ):
				self._meta_information[:] = value.split(u'\n')
			self.set_dirty_meta_information()

		def fdel(self):
			self.meta_information = u''

		return locals()
	meta_information = property(**meta_information())

	def headings():
		u""" List of top level headings """
		def fget(self):
			return self._headings

		def fset(self, value):
			self._headings[:] = value

		def fdel(self):
			del self.headings[:]

		return locals()
	headings = property(**headings())

	def write(self):
		u""" write the document

		:returns:	True if something was written, otherwise False
		"""
		raise NotImplementedError(u'Abstract method, please use concrete impelementation!')

	def set_dirty_meta_information(self):
		u""" Mark the meta information dirty so that it will be rewritten when
		saving the document """
		self._dirty_meta_information = True

	def set_dirty_document(self):
		u""" Mark the whole document dirty. When changing a heading this
		method must be executed in order to changed computation of start and
		end positions from a static to a dynamic computation """
		self._dirty_document = True

	@property
	def is_dirty(self):
		u"""
		Return information about unsaved changes for the document and all
		related headings.

		:returns:	 Return True if document contains unsaved changes.
		"""
		if self.is_dirty_meta_information:
			return True

		if self.is_dirty_document:
			return True

		if self._deleted_headings:
			return True

		return False

	@property
	def is_dirty_meta_information(self):
		u""" Return True if the meta information is marked dirty """
		return self._dirty_meta_information

	@property
	def is_dirty_document(self):
		u""" Return True if the document is marked dirty """
		return self._dirty_document

	def all_headings(self):
		u""" Iterate over all headings of the current document in serialized
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

	def find_heading(self, position=0, direction=Direction.FORWARD, \
			heading=Heading, connect_with_document=True):
		u""" Find heading in the given direction

		:postition: starting line, counting from 0 (in vim you start
				counting from 1, don't forget)
		:direction: downwards == Direction.FORWARD,
				upwards == Direction.BACKWARD
		:heading:   Heading class from which new heading objects will be
				instanciated
		:connect_with_document: if True, the newly created heading will be
				connected with the document, otherwise not

		:returns:	New heading object or None
		"""
		len_cb = len(self._content)

		if position < 0 or position > len_cb:
			return

		tmp_line = position
		start = None
		end = None

		# Search heading upwards
		if direction == Direction.FORWARD:
			while tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) is not None:
					if start is None:
						start = tmp_line
					elif end is None:
						end = tmp_line - 1
					if start is not None and end is not None:
						break
				tmp_line += 1
		else:
			while tmp_line >= 0 and tmp_line < len_cb:
				if heading.identify_heading(self._content[tmp_line]) is not None:
					if start is None:
						start = tmp_line
					elif end is None:
						end = tmp_line - 1
					if start is not None and end is not None:
						break
				tmp_line -= 1 if start is None else -1

		if start is not None and end is None:
			end = len_cb - 1
		if start is not None and end is not None:
			return heading.parse_heading_from_data(self._content[start:end + 1], self.get_all_todo_states(), \
					document=self if connect_with_document else None, orig_start=start)


# vim: set noexpandtab:
