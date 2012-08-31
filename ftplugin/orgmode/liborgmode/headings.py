# -*- coding: utf-8 -*-

"""
	headings
	~~~~~~~~~

	TODO: explain this :)
"""

import re
from UserList import UserList

from orgmode.liborgmode.base import MultiPurposeList
from orgmode.liborgmode.orgdate import OrgTimeRange
from orgmode.liborgmode.orgdate import get_orgdate
from orgmode.exceptions import HeadingDomError


REGEX_HEADING = re.compile(
		r'^(?P<level>\*+)(\s+(?P<title>.*?))?\s*(\s(?P<tags>:[\w_:@]+:))?$',
		flags=re.U | re.L)
REGEX_TAGS = re.compile(r'^\s*((?P<title>[^\s]*?)\s+)?(?P<tags>:[\w_:@]+:)$',
		flags=re.U | re.L)
REGEX_TODO = re.compile(r'^[^\s]*$')

def parse_heading(func):
	""" Parse heading on demand
	"""
	def parse(self, *args, **kwargs):
		if self._heading:
			self.parse_heading(self, *args, **kwargs)
		return func(self, *args, **kwargs)
	return parse

class LinkedTreeList(object):
	""" Implementation of a double linked list with a tree structure:
		e1 - e2 - e3
		 |    | /
		 |   e4
		 | /
		e5 - e6
	"""

	def __init__(self):
		self._parent = None
		self._next_sibling = None
		self._children = None

	def appendchild(self, heading):
		if not self.children:
			self.children = heading
			heading._next_sibling = None
		else:
			last_child = self.last_child
			last_child._next_sibling = heading
			heading._next_sibling = None
		heading._parent = self.parent
		heading._document = self.document
		return heading


	def appendsibling(self, heading):
		next_sibling = self.next_sibling
		if next_sibling:
			heading._next_sibling = next_sibling
		else:
			heading._next_sibling = None
		self._next_sibling = heading
		heading._parent = self.parent
		heading._document = self.document

	def get_index_in_parent_list(self):
		""" Retrieve the index value of current heading in the parents list of
		headings. This works also for top level headings.

		:returns:	Index value or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		idx = 0
		h = None
		if self.parent:
			h = self.parent.first_child
		elif self.document:
			h = self.document.headings

		while h and h != self:
			idx += 1
			h = h.next_heading
		if not h:
			raise HeadingDomError(u'Heading not in parent list: %s' % self)
		return idx

	def get_parent_list(self):
		""" Retrieve the parents list of headings. This works also for top
		level headings.

		:returns:	List of headings or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			return self.parent.children
		elif self.document:
			return self.document.headings

	@property
	def parent(self):
		u""" Access to the parent heading """
		return self._parent

	@property
	def number_of_parents(self):
		u""" Access to the number of parent headings before reaching the root
		document """
		def count_parents(h):
			if h.parent:
				return 1 + count_parents(h.parent)
			else:
				return 0
		return count_parents(self)

	@property
	def previous_sibling(self):
		u""" Access to the previous heading that's a sibling of the current one
		"""
		heading = None
		if self.parent:
			heading = self.parent.children
		elif self.document:
			heading = self.document.headings
		while heading:
			if heading.next_sibling == self:
				return heading
			heading = heading.next_sibling
		raise HeadingDomError(u'Heading not found in parent\'s list of children: %s' % self)


	@property
	def next_sibling(self):
		u""" Access to the next heading that's a sibling of the current one """
		return self._next_sibling

	@property
	def previous_heading(self):
		u""" Serialized access to the previous heading """
		if self.previous_sibling:
			h = self.previous_sibling
			if h.children:
				h = h.last_grandchild
			return h
		elif self.parent:
			return self.parent

	@property
	def next_heading(self):
		u""" Serialized access to the next heading """
		if self.children:
			return self.children
		elif self.next_sibling:
			return self.next_sibling
		# find the next heading by moving up the pedigree
		h = self.parent
		while h:
			if h.next_sibling:
				return h.next_sibling
			else:
				h = h.parent

	def children():
		u""" Subheadings of the current heading """
		def fget(self):
			return self._children

		def fset(self, child):
			self._children = child
			if child:
				child._parent = self
				child._next_sibling = None
				child._document = self.document

		def fdel(self):
			self._children = None

		return locals()
	children = property(**children())

	@property
	def first_child(self):
		u""" Access to the first child heading or None if no children exist """
		return self.children

	@property
	def last_child(self):
		u""" Access to the last child heading or None if no children exist """
		child = self.first_child
		while child:
			sibling = child.next_sibling
			if sibling:
				child = sibling
			else:
				return child

	@property
	def last_grandchild(self):
		u""" Access to the last child heading or None if no children exist """
		child = self.last_child
		while child:
			last_child = child.last_child
			if last_child:
				child = last_child
			else:
				return child

class Heading(LinkedTreeList):
	u""" Structural heading object """

	def __init__(self, level=1, title=u'', tags=None, todo=None, heading=None,
			body=None, active_date=None):
		u"""
		:level:		Level of the heading
		:title:		Title of the heading
		:tags:		Tags of the heading
		:todo:		Todo state of the heading
		:heading:	The elements of title, tags and todo can also be parsed
					from a heading string on demand
		:body:		Body of the heading
		:active_date: active date that is used in the agenda
		"""
		LinkedTreeList.__init__(self)

		self._document = None
		# self._parent = None
		# self._previous_sibling = None
		# self._next_sibling = None
		# self._children = HeadingList(obj=self)
		# self._next = None
		self._orig_start = None
		self._orig_len = 0

		self._dirty_heading = False
		self._level = level

		# todo
		self._todo = None
		if todo:
			self.todo = todo

		# tags
		self._tags = MultiPurposeList(on_change=self.set_dirty_heading)
		if tags:
			self.tags = tags

		# title
		self._title = u''
		if title:
			self.title = title

		# heading
		self._heading = heading
		if self._todo or self._title or self._tags:
			self._heading = None

		# body
		self._dirty_body = False
		self._body = MultiPurposeList(on_change=self.set_dirty_body)
		if body:
			self.body = body

		# active date
		self._active_date = active_date
		if active_date:
			self.active_date = active_date

	def __unicode__(self):
		# TODO check if this really works well
		if self._heading:
			return self._heading

		res = u'*' * self.level
		if self.todo:
			res = u' '.join((res, self.todo))
		if self.title:
			res = u' '.join((res, self.title))

		# compute position of tags
		if self.tags:
			tabs = 0
			spaces = 2
			tags = (u':%s:' % (u':'.join(self.tags)))

			ts = 8
			tag_column = 77
			if self.document:
				ts = self.document.tabstop
				tag_column = self.document.tag_column

			len_heading = len(res)
			len_tags = len(tags)
			if len_heading + spaces + len_tags < tag_column:
				spaces_to_next_tabstop = ts - divmod(len_heading, ts)[1]

				if len_heading + spaces_to_next_tabstop + len_tags < tag_column:
					tabs, spaces = divmod(tag_column -
							(len_heading + spaces_to_next_tabstop + len_tags), ts)

					if spaces_to_next_tabstop:
						tabs += 1
				else:
					spaces = tag_column - (len_heading + len_tags)

			res += u'\t' * tabs + u' ' * spaces + tags

		# append a trailing space when there are just * and no text
		if len(res) == self.level:
			res += u' '
		return res

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def __len__(self):
		# 1 is for the heading's title
		return 1 + len(self.body)

	def __lt__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date < other.active_date:
				return True
			elif self.active_date == other.active_date:
				return False
			elif self.active_date > other.active_date:
				return False
		except:
			if self.active_date and not other.active_date:
				return True
			elif not self.active_date and other.active_date:
				return False
			elif not self.active_date and not other.active:
				return False

	def __le__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date < other.active_date:
				return True
			elif self.active_date == other.active_date:
				return True
			elif self.active_date > other.active_date:
				return False
		except:
			if self.active_date and not other.active_date:
				return True
			elif not self.active_date and other.active_date:
				return False
			elif not self.active_date and not other.active:
				return True

	def __ge__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date > other.active_date:
				return True
			elif self.active_date == other.active_date:
				return True
			elif self.active_date < other.active_date:
				return False
		except:
			if not self.active_date and other.active_date:
				return True
			elif self.active_date and not other.active_date:
				return False
			elif not self.active_date and not other.active:
				return True

	def __gt__(self, other):
		"""
		Headings can be sorted by date.
		"""
		try:
			if self.active_date > other.active_date:
				return True
			elif self.active_date == other.active_date:
				return False
			elif self.active_date < other.active_date:
				return False
		except:
			if not self.active_date and other.active_date:
				return True
			elif self.active_date and not other.active_date:
				return False
			elif not self.active_date and not other.active:
				return False

	def copy(self, including_children=True, parent=None):
		u"""
		Create a copy of the current heading. The heading will be completely
		detached and not even belong to a document anymore.

		:including_children:	If True a copy of all children is create as
								well. If False the returned heading doesn't
								have any children.
		:parent:				Don't use this parameter. It's set
								automatically.
		"""
		heading = self.__class__(level=self.level, title=self.title, \
				tags=self.tags, todo=self.todo, body=self.body[:])
		if parent:
			parent.children.append(heading)
		if including_children and self.children:
			for item in self.children:
				item.copy(including_children=including_children, \
						parent=heading)
		heading._orig_start = self._orig_start
		heading._orig_len = self._orig_len

		heading._dirty_heading = self.is_dirty_heading

		return heading

	def parse_heading(self):
		if not self._heading:
			return self

		level = todo = title = tags = -1

		word = u''
		sndword = u''
		for c in self._heading:
			if level == -1:
				if c == u'*':
					word += c
				elif c in (u'\t', u' '):
					# finish level
					level = len(word)
				else:
					raise ValueError(u'Data doesn\'t start with a heading definition.')
			elif todo == -1:
				if c in (u'\t', u' '):
					if not word:
						# ignore whitespace
						pass
					else:
						# finish todo
						if word in allowed_todo_states:
							todo = word
						else:
							todo = None
			elif title == -1:
				if sndword:
					if c in (u'\t', u' '):
						# it's not a tag word!
						word = sndword
						sndword = word
					else:
						sndword += c
				elif c == u':':
					sndword += c
				else:
					word += c
		if todo == -1:
			todo = None
		if sndword:
			if sndword[-1] == u':':
				tags = sndword.split(u':')
			else:
				word += sndword
				sndword = u''
		title = word.strip()

		# self.level = level
		self.todo = todo
		self.title = title
		self.tags = tags

		self._heading = None
		return self

	@classmethod
	def parse_heading_from_data(cls, data, allowed_todo_states, document=None,
			orig_start=None):
		u""" Construct a new heading from the provided data

		:data:			List of lines
		:allowed_todo_states: TODO???
		:document:		The document object this heading belongs to
		:orig_start:	The original start of the heading in case it was read
						from a document. If orig_start is provided, the
						resulting heading will not be marked dirty.

		:returns:	The newly created heading
		"""
		# test_not_empty = lambda x: x != u''
		def parse_title(heading_line):
			level = todo = title = tags = -1

			word = u''
			sndword = u''
			for c in heading_line:
				if level != -1:
					return level
				if level == -1:
					if c == u'*':
						word += c
					elif c in (u'\t', u' '):
						# finish level
						level = len(word)
					else:
						raise ValueError(u'Data doesn\'t start with a heading definition.')
				# FIXME breaks further execution
				elif todo == -1:
					if c in (u'\t', u' '):
						if not word:
							# ignore whitespace
							pass
						else:
							# finish todo
							if word in allowed_todo_states:
								todo = word
							else:
								todo = None
				elif title == -1:
					if sndword:
						if c in (u'\t', u' '):
							# it's not a tag word!
							word = sndword
							sndword = word
						else:
							sndword += c
					elif c == u':':
						sndword += c
					else:
						word += c
			if todo == -1:
				todo = None
			if sndword:
				if sndword[-1] == u':':
					tags = sndword.split(u':')
				else:
					word += sndword
					sndword = u''
			title = word.strip()
			return (level, todo, title, tags)

			# WARNING this regular expression fails if there is just one or no
			# word in the heading but a tag!
			m = REGEX_HEADING.match(heading_line)
			if m:
				r = m.groupdict()
				level = len(r[u'level'])
				todo = None
				title = u''
				tags = filter(test_not_empty, r[u'tags'].split(u':')) if r[u'tags'] else []

				# if there is just one or no word in the heading, redo the parsing
				mt = REGEX_TAGS.match(r[u'title'])
				if not tags and mt:
					r = mt.groupdict()
					tags = filter(test_not_empty, r[u'tags'].split(u':')) if r[u'tags'] else []
				if r[u'title'] is not None:
					_todo_title = [i.strip() for i in r[u'title'].split(None, 1)]
					if _todo_title and _todo_title[0] in allowed_todo_states:
						todo = _todo_title[0]
						if len(_todo_title) > 1:
							title = _todo_title[1]
					else:
						title = r[u'title'].strip()

				return (level, todo, title, tags)
			raise ValueError(u'Data doesn\'t start with a heading definition.')

		if not data:
			raise ValueError(u'Unable to create heading, no data provided.')

		# create new heaing
		new_heading = cls(heading=data[0])
		new_heading.level = parse_title(data[0])
		# new_heading.level, new_heading.todo, new_heading.title, new_heading.tags = parse_title(data[0])
		new_heading.body = data[1:]
		if orig_start is not None:
			new_heading._dirty_heading = False
			new_heading._dirty_body = False
			new_heading._orig_start = orig_start
			new_heading._orig_len = len(new_heading)
		if document:
			new_heading._document = document

		# try to find active dates
		#tmp_orgdate = get_orgdate(data)
		#if tmp_orgdate and tmp_orgdate.active \
		#		and not isinstance(tmp_orgdate, OrgTimeRange):
		#	new_heading.active_date = tmp_orgdate
		#else:
		#	new_heading.active_date = None

		return new_heading

	@classmethod
	def identify_heading(cls, line):
		u""" Test if a certain line is a heading or not.

		:line: the line to check

		:returns: level
		"""
		level = 0
		for c in line:
			if c == u'*':
				level += 1
			elif c in (u'\t', u' ') and level:
				return level
			else:
				return None

	@property
	def end_of_last_child(self):
		u""" Access to end of the last child """
		if self.children:
			return self.last_grandchild.end
		return self.end

	@property
	def end_of_last_child_vim(self):
		return self.end_of_last_child + 1

	@property
	def is_dirty(self):
		u""" Return True if the heading's body is marked dirty """
		return self._dirty_heading or self._dirty_body

	@property
	def is_dirty_heading(self):
		u""" Return True if the heading is marked dirty """
		return self._dirty_heading

	@property
	def is_dirty_body(self):
		u""" Return True if the heading's body is marked dirty """
		return self._dirty_body

	def set_dirty(self):
		u""" Mark the heading and body dirty so that it will be rewritten when
		saving the document """
		self._dirty_heading = True
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_heading(self):
		u""" Mark the heading dirty so that it will be rewritten when saving the
		document """
		self._dirty_heading = True
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_body(self):
		u""" Mark the heading's body dirty so that it will be rewritten when
		saving the document """
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	@property
	def document(self):
		u""" Read only access to the document. If you want to change the
		document, just assign the heading to another document """
		return self._document

	@property
	def start(self):
		u""" Access to the starting line of the heading """
		if self.document is None:
			return self._orig_start

		# static computation of start
		if not self.document.is_dirty:
			return self._orig_start

		# dynamic computation of start, really slow!
		def compute_start(h):
			if h:
				return len(h) + compute_start(h.previous_heading)
			return len(self.document.meta_information) if \
					self.document.meta_information else 0
		return compute_start(self.previous_heading)

	@property
	def start_vim(self):
		if self.start is not None:
			return self.start + 1

	@property
	def end(self):
		u""" Access to the ending line of the heading """
		if self.start is not None:
			return self.start + len(self.body)

	@property
	def end_vim(self):
		if self.end is not None:
			return self.end + 1

	def level():
		u""" Access to the heading level """
		def fget(self):
			return self._level

		def fset(self, value):
			self._level = int(value)
			self.set_dirty_heading()

		def fdel(self):
			self.level = None

		return locals()
	level = property(**level())

	def todo():
		u""" Todo state of current heading. When todo state is set, it will be
		converted to uppercase """
		@parse_heading
		def fget(self):
			# extract todo state from heading
			return self._todo

		@parse_heading
		def fset(self, value):
			# update todo state
			if type(value) not in (unicode, str, type(None)):
				raise ValueError(u'Todo state must be a string or None.')
			if value and not REGEX_TODO.match(value):
				raise ValueError(u'Found non allowed character in todo state! %s' % value)
			if not value:
				self._todo = None
			else:
				v = value
				if type(v) == str:
					v = v.decode(u'utf-8')
				self._todo = v.upper()
			self.set_dirty_heading()

		def fdel(self):
			self.todo = None

		return locals()
	todo = property(**todo())

	def active_date():
		u"""
		active date of the hearing.

		active dates are used in the agenda view. they can be part of the
		heading and/or the body.
		"""
		def fget(self):
			return self._active_date

		def fset(self, value):
			self._active_date = value

		def fdel(self):
			self._active_date = None
		return locals()
	active_date = property(**active_date())

	def title():
		u""" Title of current heading """
		@parse_heading
		def fget(self):
			return self._title.strip()

		@parse_heading
		def fset(self, value):
			if type(value) not in (unicode, str):
				raise ValueError(u'Title must be a string.')
			v = value
			if type(v) == str:
				v = v.decode(u'utf-8')
			self._title = v.strip()
			self.set_dirty_heading()

		def fdel(self):
			self.title = u''

		return locals()
	title = property(**title())

	def tags():
		u""" Tags of the current heading """
		@parse_heading
		def fget(self):
			return self._tags

		@parse_heading
		def fset(self, value):
			v = value
			if type(v) in (unicode, str):
				v = list(unicode(v))
			if type(v) not in (list, tuple) and not isinstance(v, UserList):
				v = list(unicode(v))
			v_decoded = []
			for i in v:
				if type(i) not in (unicode, str):
					raise ValueError(u'Found non string value in tags! %s' % unicode(i))
				if u':' in i:
					raise ValueError(u'Found non allowed character in tag! %s' % i)
				i_tmp = i.strip().replace(' ', '_').replace('\t', '_')
				if type(i) == str:
					i_tmp = i.decode(u'utf-8')
				v_decoded.append(i_tmp)

			self._tags[:] = v_decoded

		def fdel(self):
			self.tags = []

		return locals()
	tags = property(**tags())

	def body():
		u""" Holds the content belonging to the heading """
		def fget(self):
			return self._body

		def fset(self, value):
			if type(value) in (list, tuple) or isinstance(value, UserList):
				self._body[:] = value
			elif type(value) in (str, ):
				self._body[:] = value.decode('utf-8').split(u'\n')
			elif type(value) in (unicode, ):
				self._body[:] = value.split(u'\n')
			else:
				self.body = list(unicode(value))

		def fdel(self):
			self.body = []

		return locals()
	body = property(**body())

# vim: set noexpandtab:
