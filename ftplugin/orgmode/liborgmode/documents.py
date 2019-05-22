# -*- coding: utf-8 -*-

"""
	documents
	~~~~~~~~~

	TODO: explain this :)
"""

try:
	from collections import UserList
except:
	from UserList import UserList

from orgmode import settings

from orgmode.liborgmode.base import MultiPurposeList, flatten_list, Direction, get_domobj_range
from orgmode.liborgmode.headings import Heading, HeadingList

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *

import re
REGEX_LOGGING_MODIFIERS = re.compile(r"[!@/]")

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

		# is a list - only the Document methods should work on this list!
		self._content = None
		self._dirty_meta_information = False
		self._dirty_document = False
		self._meta_information = MultiPurposeList(
			on_change=self.set_dirty_meta_information)
		self._orig_meta_information_len = None
		self._headings = HeadingList(obj=self)
		self._deleted_headings = []

		# settings needed to align tags properly
		self._tabstop = 8
		self._tag_column = 77

		# TODO this doesn't differentiate between ACTIVE and FINISHED todo's
		self.todo_states_stripped = self.get_settings_todo_states(True)
		self.todo_states = self.get_settings_todo_states(False)

	def __unicode__(self):
		if self.meta_information is None:
			return u'\n'.join(self.all_headings())
		return u'\n'.join(self.meta_information) + u'\n' + u'\n'.join([u'\n'.join([unicode(i)] + i.body) for i in self.all_headings()])

	def __str__(self):
		return u_encode(self.__unicode__())

	def get_done_states(self, strip_access_key=True):
		all_states = self.get_todo_states(strip_access_key)
		done_states =  list([ done_state for x in all_states for done_state in x[1]])

		return done_states

	def parse_todo_settings(self, setting, strip_access_key = True):
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
							_i = REGEX_LOGGING_MODIFIERS.sub("", _i)
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
		return parse_states(setting)


	def get_settings_todo_states(self, strip_access_key=True):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		:returns:	[([todo states], [done states]), ..]
		"""
		states = settings.get(u'org_todo_keywords', [])

		if type(states) not in (list, tuple):
			return []

		return self.parse_todo_settings(states, strip_access_key)

	def get_all_todo_states(self):
		u""" Convenience function that returns all todo and done states and
		sequences in one big list.

		Returns:
			list: [all todo/done states]
		"""
		# TODO This is not necessary remove
		return flatten_list(self.get_todo_states())

	def get_todo_states(self, strip_access_key=True):
		u""" Returns a list containing a tuple of two lists of allowed todo
		states split by todo and done states. Multiple todo-done state
		sequences can be defined.

		Returns:
			list: [([todo states], [done states]), ..]
		"""
		# TODO this should be made into property so todo states can be set like
		# this too.. or there was also some todo property around... oh well..
		# TODO there is the same method in vimbuffer

		ret = self.todo_states
		if strip_access_key:
		    ret = self.todo_states_stripped

		return ret

	@property
	def tabstop(self):
		u""" Tabstop for this document """
		return self._tabstop

	@tabstop.setter
	def tabstop(self, value):
		self._tabstop = value

	@property
	def tag_column(self):
		u""" The column all tags are right-aligned to """
		return self._tag_column

	@tag_column.setter
	def tag_column(self, value):
		self._tag_column = value

	def init_dom(self, heading=Heading):
		u""" Initialize all headings in document - build DOM. This method
		should be call prior to accessing the document.

		Returns:
			self
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

	@property
	def meta_information(self):
		u""" Meta information is text that precedes all headings in an org-mode
		document. It might contain additional information about the document,
		e.g. author
		"""
		return self._meta_information

	@meta_information.setter
	def meta_information(self, value):
		if self._orig_meta_information_len is None:
			self._orig_meta_information_len = len(self.meta_information)
		if type(value) in (list, tuple) or isinstance(value, UserList):
			self._meta_information[:] = flatten_list(value)
		elif type(value) in (str, ):
			self._meta_information[:] = u_decode(value).split(u'\n')
		elif type(value) in (unicode, ):
			self._meta_information[:] = value.split(u'\n')
		self.set_dirty_meta_information()

	@meta_information.deleter
	def meta_information(self):
		self.meta_information = u''

	@property
	def headings(self):
		u""" List of top level headings """
		return self._headings

	@headings.setter
	def headings(self, value):
		self._headings[:] = value

	@headings.deleter
	def headings(self):
		del self.headings[:]

	def write(self):
		u""" Write the document

		Returns:
			bool: True if something was written, otherwise False
		"""
		raise NotImplementedError(u'Abstract method, please use concrete impelementation!')

	def set_dirty_meta_information(self):
		u""" Mark the meta information dirty.

		Note:
			Causes meta information to be rewritten when saving the document
		"""
		self._dirty_meta_information = True

	def set_dirty_document(self):
		u""" Mark the whole document dirty.

		Note:
			When changing a heading this method must be executed in order to
			changed computation of start and end positions from a static to a
			dynamic computation
		"""
		self._dirty_document = True

	@property
	def is_dirty(self):
		u""" Return information about unsaved changes for the document and all
		related headings.

		Returns:
			bool: True if document contains unsaved changes.
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
			return

		h = self.headings[0]
		while h:
			yield h
			h = h.next_heading
		return

	def find_heading(
		self, position=0, direction=Direction.FORWARD, heading=Heading,
		connect_with_document=True):
		u""" Find heading in the given direction

		Args:
			position (int): starting line, counting from 0 (in vim you start
					counting from 1, don't forget)
			direction: downwards == Direction.FORWARD,
					upwards == Direction.BACKWARD
			heading:   Heading class from which new heading objects will be
					instanciated
			connect_with_document: if True, the newly created heading will be
					connected with the document, otherwise not

		Returns:
			heading or None: New heading
		"""
		start, end = get_domobj_range(
			content=self._content, position=position, direction=direction,
			identify_fun=heading.identify_heading)

		if start is None:
			return None

		if end is None:
			end = len(self._content) - 1

		document = self if connect_with_document else None

		return heading.parse_heading_from_data(
			self._content[start:end + 1], self.get_all_todo_states(),
			document=document, orig_start=start)


# vim: set noexpandtab:
