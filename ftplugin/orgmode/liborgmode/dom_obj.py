# -*- coding: utf-8 -*-

"""
	dom object
	~~~~~~~~~~

	TODO: explain this :)
"""

import re
from UserList import UserList
from orgmode.liborgmode.base import MultiPurposeList, flatten_list

# breaking down tasks regex
REGEX_SUBTASK = re.compile(r'\[(\d*)/(\d*)\]')
REGEX_SUBTASK_PERCENT = re.compile(r'\[(\d*)%\]')

# heading regex
REGEX_HEADING = re.compile(
	r'^(?P<level>\*+)(\s+(?P<title>.*?))?\s*(\s(?P<tags>:[\w_:@]+:))?$',
	flags=re.U | re.L)
REGEX_TAG = re.compile(
	r'^\s*((?P<title>[^\s]*?)\s+)?(?P<tags>:[\w_:@]+:)$',
	flags=re.U | re.L)
REGEX_TODO = re.compile(r'^[^\s]*$')

# checkbox regex:
#   - [ ] checkbox item
# - [X] checkbox item
# - [ ]
# - no status checkbox
UnOrderListType = [u'-', u'+', u'*']
OrderListType = [u'.', u')']
REGEX_CHECKBOX = re.compile(
	r'^(?P<level>\s*)(?P<type>[%s]|([a-zA-Z]|[\d]+)[%s])(\s+(?P<status>\[.\]))?\s*(?P<title>.*)$'
	% (''.join(UnOrderListType), ''.join(OrderListType)), flags=re.U | re.L)


class DomObj(object):
	u"""
	A DomObj is DOM structure element, like Heading and Checkbox.
	Its purpose is to abstract the same parts of Heading and Checkbox objects,
	and make code reusable.

	All methods and properties are extracted from Heading object.
	Heading and Checkbox objects inherit from DomObj, and override some specific
	methods in their own objects.

	Normally, we don't intend to use DomObj directly. However, we can add some more
	DOM structure element based on this class to make code more concise.
	"""

	def __init__(self, level=1, title=u'', body=None):
		u"""
		:level:		Level of the dom object
		:title:		Title of the dom object
		:body:		Body of the dom object
		"""
		object.__init__(self)

		self._document = None
		self._parent = None
		self._previous_sibling = None
		self._next_sibling = None
		self._children = MultiPurposeList()
		self._orig_start = None
		self._orig_len = 0

		self._level = level
		# title
		self._title = u''
		if title:
			self.title = title

		# body
		self._dirty_body = False
		self._body = MultiPurposeList(on_change=self.set_dirty_body)
		if body:
			self.body = body

	def __unicode__(self):
		return u'<dom obj level=%s, title=%s>' % (level, title)

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def __len__(self):
		# 1 is for the heading's title
		return 1 + len(self.body)

	@property
	def is_dirty(self):
		u""" Return True if the dom obj body is marked dirty """
		return self._dirty_body

	@property
	def is_dirty_body(self):
		u""" Return True if the dom obj body is marked dirty """
		return self._dirty_body

	def get_index_in_parent_list(self):
		""" Retrieve the index value of current dom obj in the parents list of
		dom objs. This works also for top level dom objs.

		:returns:	Index value or None if dom obj doesn't have a
					parent/document or is not in the list of dom objs
		"""
		l = self.get_parent_list()
		if l:
			return l.index(self)

	def get_parent_list(self):
		""" Retrieve the parents list of dom objs. This works also for top
		level dom objs.

		:returns:	List of dom objs or None if dom objs doesn't have a
					parent/document or is not in the list of dom objs
		"""
		if self.parent:
			if self in self.parent.children:
				return self.parent.children

	def set_dirty(self):
		u""" Mark the dom objs and body dirty so that it will be rewritten when
		saving the document """
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_body(self):
		u""" Mark the dom objs' body dirty so that it will be rewritten when
		saving the document """
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	@property
	def document(self):
		u""" Read only access to the document. If you want to change the
		document, just assign the dom obj to another document """
		return self._document

	@property
	def parent(self):
		u""" Access to the parent dom obj """
		return self._parent

	@property
	def number_of_parents(self):
		u""" Access to the number of parent dom objs before reaching the root
		document """
		def count_parents(h):
			if h.parent:
				return 1 + count_parents(h.parent)
			else:
				return 0
		return count_parents(self)

	@property
	def previous_sibling(self):
		u""" Access to the previous dom obj that's a sibling of the current one
		"""
		return self._previous_sibling

	@property
	def next_sibling(self):
		u""" Access to the next dom obj that's a sibling of the current one """
		return self._next_sibling

	@property
	def previous_item(self):
		u""" Serialized access to the previous dom obj """
		if self.previous_sibling:
			h = self.previous_sibling
			while h.children:
				h = h.children[-1]
			return h
		elif self.parent:
			return self.parent

	@property
	def next_item(self):
		u""" Serialized access to the next dom obj """
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
		u""" Access to the starting line of the dom obj """
		if self.document is None:
			return self._orig_start

		# static computation of start
		if not self.document.is_dirty:
			return self._orig_start

		# dynamic computation of start, really slow!
		def compute_start(h):
			if h:
				return len(h) + compute_start(h.previous_item)
		return compute_start(self.previous_item)

	@property
	def start_vim(self):
		if self.start is not None:
			return self.start + 1

	@property
	def end(self):
		u""" Access to the ending line of the dom obj """
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
		u""" Subheadings of the current dom obj """
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
		u""" Access to the first child dom obj or None if no children exist """
		if self.children:
			return self.children[0]

	@property
	def last_child(self):
		u""" Access to the last child dom obj or None if no children exist """
		if self.children:
			return self.children[-1]

	def level():
		u""" Access to the dom obj level """
		def fget(self):
			return self._level

		def fset(self, value):
			self._level = int(value)
			self.set_dirty()

		def fdel(self):
			self.level = None

		return locals()
	level = property(**level())

	def title():
		u""" Title of current dom object """
		def fget(self):
			return self._title.strip()

		def fset(self, value):
			if type(value) not in (unicode, str):
				raise ValueError(u'Title must be a string.')
			v = value
			if type(v) == str:
				v = v.decode(u'utf-8')
			self._title = v.strip()
			self.set_dirty()

		def fdel(self):
			self.title = u''

		return locals()
	title = property(**title())

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


class DomObjList(MultiPurposeList):
	u"""
	A Dom Obj List
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
	def is_domobj(cls, obj):
		return isinstance(obj, DomObj)

	def _get_document(self):
		if self.__class__.is_domobj(self._obj):
			return self._obj._document
		return self._obj

	def __setitem__(self, i, item):
		if not self.__class__.is_domobj(item):
			raise ValueError(u'Item is not a Dom obj!')
		if item in self:
			raise ValueError(u'Dom obj is already part of this list!')
		# self._add_to_deleted_domobjs(self[i])

		# self._associate_domobj(item, \
		# self[i - 1] if i - 1 >= 0 else None, \
		# self[i + 1] if i + 1 < len(self) else None)
		MultiPurposeList.__setitem__(self, i, item)

	def __setslice__(self, i, j, other):
		o = other
		if self.__class__.is_domobj(o):
			o = (o, )
		o = flatten_list(o)
		for item in o:
			if not self.__class__.is_domobj(item):
				raise ValueError(u'List contains items that are not a Dom obj!')
		i = max(i, 0)
		j = max(j, 0)
		# self._add_to_deleted_domobjs(self[i:j])
		# self._associate_domobj(o, \
		# self[i - 1] if i - 1 >= 0 and i < len(self) else None, \
		# self[j] if j >= 0 and j < len(self) else None)
		MultiPurposeList.__setslice__(self, i, j, o)

	def __delitem__(self, i, taint=True):
		item = self[i]
		if item.previous_sibling:
			item.previous_sibling._next_sibling = item.next_sibling
		if item.next_sibling:
			item.next_sibling._previous_sibling = item.previous_sibling

		# if taint:
			# self._add_to_deleted_domobjs(item)
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
		# if taint:
			# self._add_to_deleted_domobjs(items)
		MultiPurposeList.__delslice__(self, i, j)

	def __iadd__(self, other):
		o = other
		if self.__class__.is_domobj(o):
			o = (o, )
		for item in flatten_list(o):
			if not self.__class__.is_domobj(item):
				raise ValueError(u'List contains items that are not a Dom obj!')
		# self._associate_domobj(o, self[-1] if len(self) > 0 else None, None)
		return MultiPurposeList.__iadd__(self, o)

	def __imul__(self, n):
		# TODO das müsste eigentlich ein klonen von objekten zur Folge haben
		return MultiPurposeList.__imul__(self, n)

	def append(self, item, taint=True):
		if not self.__class__.is_domobj(item):
			raise ValueError(u'Item is not a heading!')
		if item in self:
			raise ValueError(u'Heading is already part of this list!')
		# self._associate_domobj(
		# 	item, self[-1] if len(self) > 0 else None,
		# 	None, taint=taint)
		MultiPurposeList.append(self, item)

	def insert(self, i, item, taint=True):
		# self._associate_domobj(
		# 	item,
		# 	self[i - 1] if i - 1 >= 0 and i - 1 < len(self) else None,
		# 	self[i] if i >= 0 and i < len(self) else None, taint=taint)
		MultiPurposeList.insert(self, i, item)

	def pop(self, i=-1):
		item = self[i]
		# self._add_to_deleted_domobjs(item)
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
		if self.__class__.is_domobj(o):
			o = (o, )
		for item in o:
			if not self.__class__.is_domobj(item):
				raise ValueError(u'List contains items that are not a heading!')
		# self._associate_domobj(o, self[-1] if len(self) > 0 else None, None)
		MultiPurposeList.extend(self, o)


# vim: set noexpandtab:
