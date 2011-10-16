# -*- coding: utf-8 -*-

"""
	headings
	~~~~~~~~~

	TODO: explain this :)
"""

import re
from UserList import UserList

from orgmode.liborgmode.base import MultiPurposeList, flatten_list
from orgmode.liborgmode.orgdate import OrgTimeRange
from orgmode.liborgmode.orgdate import get_orgdate


REGEX_HEADING = re.compile(
		r'^(?P<level>\*+)(\s+(?P<title>.*?))?\s*(\s(?P<tags>:[\w_:@]+:))?$',
		flags=re.U | re.L)
REGEX_TAGS = re.compile(r'^\s*((?P<title>[^\s]*?)\s+)?(?P<tags>:[\w_:@]+:)$',
		flags=re.U | re.L)
REGEX_TODO = re.compile(r'^[^\s]*$')


class Heading(object):
	u""" Structural heading object """

	def __init__(self, level=1, title=u'', tags=None, todo=None, body=None,
			active_date=None):
		u"""
		:level:		Level of the heading
		:title:		Title of the heading
		:tags:		Tags of the heading
		:todo:		Todo state of the heading
		:body:		Body of the heading
		:active_date: active date that is used in the agenda
		"""
		object.__init__(self)

		self._document = None
		self._parent = None
		self._previous_sibling = None
		self._next_sibling = None
		self._children = HeadingList(obj=self)
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
		def parse_title(heading_line):
			# WARNING this regular expression fails if there is just one or no
			# word in the heading but a tag!
			m = REGEX_HEADING.match(heading_line)
			if m:
				r = m.groupdict()
				level = len(r[u'level'])
				todo = None
				title = u''
				tags = filter(lambda x: x != u'', r[u'tags'].split(u':')) if r[u'tags'] else []

				# if there is just one or no word in the heading, redo the parsing
				mt = REGEX_TAGS.match(r[u'title'])
				if not tags and mt:
					r = mt.groupdict()
					tags = filter(lambda x: x != u'', r[u'tags'].split(u':')) if r[u'tags'] else []
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
		new_heading = cls()
		new_heading.level, new_heading.todo, new_heading.title, new_heading.tags = parse_title(data[0])
		new_heading.body = data[1:]
		if orig_start is not None:
			new_heading._dirty_heading = False
			new_heading._dirty_body = False
			new_heading._orig_start = orig_start
			new_heading._orig_len = len(new_heading)
		if document:
			new_heading._document = document

		# try to find active dates
		tmp_orgdate = get_orgdate(data)
		if tmp_orgdate and tmp_orgdate.active \
				and not isinstance(tmp_orgdate, OrgTimeRange):
			new_heading.active_date = tmp_orgdate
		else:
			new_heading.active_date = None

		return new_heading

	@classmethod
	def identify_heading(cls, line):
		u""" Test if a certain line is a heading or not.

		:line: the line to check

		:returns: level
		"""
		level = 0
		if not line:
			return None
		for i in xrange(0, len(line)):
			if line[i] == u'*':
				level += 1
				if len(line) > (i + 1) and line[i + 1] in (u'\t', u' '):
					return level
			else:
				return None

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

	def get_index_in_parent_list(self):
		""" Retrieve the index value of current heading in the parents list of
		headings. This works also for top level headings.

		:returns:	Index value or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			if self in self.parent.children:
				return self.parent.children.index(self)
		elif self.document:
			if self in self.document.headings:
				return self.document.headings.index(self)

	def get_parent_list(self):
		""" Retrieve the parents list of headings. This works also for top
		level headings.

		:returns:	List of headings or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			if self in self.parent.children:
				return self.parent.children
		elif self.document:
			if self in self.document.headings:
				return self.document.headings

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
		return self._previous_sibling

	@property
	def next_sibling(self):
		u""" Access to the next heading that's a sibling of the current one """
		return self._next_sibling

	@property
	def previous_heading(self):
		u""" Serialized access to the previous heading """
		if self.previous_sibling:
			h = self.previous_sibling
			while h.children:
				h = h.children[-1]
			return h
		elif self.parent:
			return self.parent

	@property
	def next_heading(self):
		u""" Serialized access to the next heading """
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

	@property
	def end_of_last_child(self):
		u""" Access to end of the last child """
		if self.children:
			child = self.children[-1]
			while child.children:
				child = child.children[-1]
			return child.end
		return self.end

	@property
	def end_of_last_child_vim(self):
		return self.end_of_last_child + 1

	def children():
		u""" Subheadings of the current heading """
		def fget(self):
			return self._children

		def fset(self, value):
			v = value
			if type(v) in (list, tuple) or isinstance(v, UserList):
				v = flatten_list(v)
			self._children[:] = v

		def fdel(self):
			del self.children[:]

		return locals()
	children = property(**children())

	@property
	def first_child(self):
		u""" Access to the first child heading or None if no children exist """
		if self.children:
			return self.children[0]

	@property
	def last_child(self):
		u""" Access to the last child heading or None if no children exist """
		if self.children:
			return self.children[-1]

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
		def fget(self):
			# extract todo state from heading
			return self._todo

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
		def fget(self):
			return self._title.strip()

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
		def fget(self):
			return self._tags

		def fset(self, value):
			v = value
			if type(v) in (unicode, str):
				v = list(unicode(v))
			if type(v) not in (list, tuple) and not isinstance(v, UserList):
				v = list(unicode(v))
			v = flatten_list(v)
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
				self._body[:] = flatten_list(value)
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


class HeadingList(MultiPurposeList):
	u"""
	A Heading List just contains headings. It's used for documents to store top
	level headings and for headings to store subheadings.

	A Heading List must be linked to a Document or Heading!

	See documenatation of MultiPurposeList for more information.
	"""
	def __init__(self, initlist=None, obj=None):
		"""
		:initlist:	Initial data
		:obj:		Link to a concrete Heading or Document object
		"""
		# it's not necessary to register a on_change hook because the heading
		# list will itself take care of marking headings dirty or adding
		# headings to the deleted headings list
		MultiPurposeList.__init__(self)

		self._obj = obj

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
		u"""
		Serialize headings so that all subheadings are also marked for deletion
		"""
		if not self._get_document():
			# HeadingList has not yet been associated
			return

		if type(item) in (list, tuple) or isinstance(item, UserList):
			for i in flatten_list(item):
				self._add_to_deleted_headings(i)
		else:
			self._get_document()._deleted_headings.append(
					item.copy(including_children=False))
			self._add_to_deleted_headings(item.children)
			self._get_document().set_dirty_document()

	def _associate_heading(self, heading, previous_sibling, next_sibling,
			children=False, taint=True):
		"""
		:heading:		The heading or list to associate with the current heading
		:previous_sibling:	The previous sibling of the current heading. If
							heading is a list the first heading will be
							connected with the previous sibling and the last
							heading with the next sibling. The items in between
							will be linked with one another.
		:next_sibling:	The next sibling of the current heading. If
							heading is a list the first heading will be
							connected with the previous sibling and the last
							heading with the next sibling. The items in between
							will be linked with one another.
		:children:		Marks whether children are processed in the current
							iteration or not (should not be use, it's set
							automatically)
		:taint:			If not True, the heading is not marked dirty at the end
							of the association process and its orig_start and
							orig_len values are not updated.
		"""
		# TODO this method should be externalized and moved to the Heading class
		if type(heading) in (list, tuple) or isinstance(heading, UserList):
			prev = previous_sibling
			current = None
			for _next in flatten_list(heading):
				if current:
					self._associate_heading(current, prev, _next, \
							children=children, taint=taint)
					prev = current
				current = _next
			if current:
				self._associate_heading(current, prev, next_sibling, \
						children=children, taint=taint)
		else:
			if taint:
				heading._orig_start = None
				heading._orig_len = None
			d = self._get_document()
			if heading._document != d:
				heading._document = d
			if not children:
				# connect heading with previous and next headings
				heading._previous_sibling = previous_sibling
				if previous_sibling:
					previous_sibling._next_sibling = heading
				heading._next_sibling = next_sibling
				if next_sibling:
					next_sibling._previous_sibling = heading

				if d == self._obj:
					# self._obj is a Document
					heading._parent = None
				elif heading._parent != self._obj:
					# self._obj is a Heading
					heading._parent = self._obj
			if taint:
				heading.set_dirty()

			self._associate_heading(heading.children, None, None, \
					children=True, taint=taint)

	def __setitem__(self, i, item):
		if not self.__class__.is_heading(item):
			raise ValueError(u'Item is not a heading!')
		if item in self:
			raise ValueError(u'Heading is already part of this list!')
		self._add_to_deleted_headings(self[i])

		self._associate_heading(item, \
				self[i - 1] if i - 1 >= 0 else None, \
				self[i + 1] if i + 1 < len(self) else None)
		MultiPurposeList.__setitem__(self, i, item)

	def __setslice__(self, i, j, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		o = flatten_list(o)
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		i = max(i, 0)
		j = max(j, 0)
		self._add_to_deleted_headings(self[i:j])
		self._associate_heading(o, \
				self[i - 1] if i - 1 >= 0 and i < len(self) else None, \
				self[j] if j >= 0 and j < len(self) else None)
		MultiPurposeList.__setslice__(self, i, j, o)

	def __delitem__(self, i, taint=True):
		item = self[i]
		if item.previous_sibling:
			item.previous_sibling._next_sibling = item.next_sibling
		if item.next_sibling:
			item.next_sibling._previous_sibling = item.previous_sibling

		if taint:
			self._add_to_deleted_headings(item)
		MultiPurposeList.__delitem__(self, i)

	def __delslice__(self, i, j, taint=True):
		i = max(i, 0)
		j = max(j, 0)
		items = self[i:j]
		if items:
			first = items[0]
			last = items[-1]
			if first.previous_sibling:
				first.previous_sibling._next_sibling = last.next_sibling
			if last.next_sibling:
				last.next_sibling._previous_sibling = first.previous_sibling
		if taint:
			self._add_to_deleted_headings(items)
		MultiPurposeList.__delslice__(self, i, j)

	def __iadd__(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in flatten_list(o):
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		self._associate_heading(o, self[-1] if len(self) > 0 else None, None)
		return MultiPurposeList.__iadd__(self, o)

	def __imul__(self, n):
		# TODO das müsste eigentlich ein klonen von objekten zur Folge haben
		return MultiPurposeList.__imul__(self, n)

	def append(self, item, taint=True):
		if not self.__class__.is_heading(item):
			raise ValueError(u'Item is not a heading!')
		if item in self:
			raise ValueError(u'Heading is already part of this list!')
		self._associate_heading(item, self[-1] if len(self) > 0 else None, \
				None, taint=taint)
		MultiPurposeList.append(self, item)

	def insert(self, i, item, taint=True):
		self._associate_heading(item, \
				self[i - 1] if i - 1 >= 0 and i - 1 < len(self) else None,
				self[i] if i >= 0 and i < len(self) else None, taint=taint)
		MultiPurposeList.insert(self, i, item)

	def pop(self, i=-1):
		item = self[i]
		self._add_to_deleted_headings(item)
		del self[i]
		return item

	def remove_slice(self, i, j, taint=True):
		self.__delslice__(i, j, taint=taint)

	def remove(self, item, taint=True):
		self.__delitem__(self.index(item), taint=taint)

	def reverse(self):
		MultiPurposeList.reverse(self)
		prev_h = None
		for h in self:
			h._previous_sibling = prev_h
			h._next_sibling = None
			prev_h._next_sibling = h
			h.set_dirty()
			prev_h = h

	def sort(self, *args, **kwds):
		MultiPurposeList.sort(*args, **kwds)
		prev_h = None
		for h in self:
			h._previous_sibling = prev_h
			h._next_sibling = None
			prev_h._next_sibling = h
			h.set_dirty()
			prev_h = h

	def extend(self, other):
		o = other
		if self.__class__.is_heading(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_heading(item):
				raise ValueError(u'List contains items that are not a heading!')
		self._associate_heading(o, self[-1] if len(self) > 0 else None, None)
		MultiPurposeList.extend(self, o)


# vim: set noexpandtab:
