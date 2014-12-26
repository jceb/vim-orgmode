# -*- coding: utf-8 -*-

"""
	checkboxes
	~~~~~~~~~

	TODO: explain this :)
"""

import re
from UserList import UserList

import vim
from orgmode.liborgmode.base import MultiPurposeList, flatten_list
from orgmode.liborgmode.orgdate import OrgTimeRange
from orgmode.liborgmode.orgdate import get_orgdate
from orgmode.liborgmode.dom_obj import DomObj, DomObjList, REGEX_SUBTASK, REGEX_SUBTASK_PERCENT, REGEX_HEADING, REGEX_CHECKBOX


class Checkbox(DomObj):
	u""" Structural checkbox object """
	STATUS_ON = u'[X]'
	STATUS_OFF = u'[ ]'
	# intermediate status
	STATUS_INT = u'[-]'

	def __init__(self, level=1, type=u'-', title=u'', status=u'[ ]', body=None):
		u"""
		:level:		Indent level of the checkbox
		:type:		Type of the checkbox list (-, +, *)
		:title:		Title of the checkbox
		:status:	Status of the checkbox ([ ], [X], [-])
		:body:		Body of the checkbox
		"""
		DomObj.__init__(self, level=level, title=title, body=body)

		# heading
		self._heading = None

		self._children = CheckboxList(obj=self)
		self._dirty_checkbox = False
		# list type
		self._type = u'-'
		if type:
			self.type = type
		# status
		self._status = Checkbox.STATUS_OFF
		if status:
			self.status = status

	def __unicode__(self):
		return u' ' * self.level + self.type + u' ' + \
			(self.status + u' ' if self.status else u'') + self.title

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def __len__(self):
		# 1 is for the heading's title
		return 1 + len(self.body)

	def copy(self, including_children=True, parent=None):
		u"""
		Create a copy of the current checkbox. The checkbox will be completely
		detached and not even belong to a document anymore.

		:including_children:	If True a copy of all children is create as
								well. If False the returned checkbox doesn't
								have any children.
		:parent:				Don't use this parameter. It's set
								automatically.
		"""
		checkbox = self.__class__(
			level=self.level, title=self.title,
			body=self.body[:])
		if parent:
			parent.children.append(checkbox)
		if including_children and self.children:
			for item in self.children:
				item.copy(
					including_children=including_children,
					parent=checkbox)
		checkbox._orig_start = self._orig_start
		checkbox._orig_len = self._orig_len

		checkbox._dirty_heading = self.is_dirty_checkbox

		return checkbox

	@classmethod
	def parse_checkbox_from_data(cls, data, heading=None, orig_start=None):
		u""" Construct a new checkbox from the provided data

		:data:			List of lines
		:heading:		The heading object this checkbox belongs to
		:orig_start:	The original start of the heading in case it was read
						from a document. If orig_start is provided, the
						resulting heading will not be marked dirty.

		:returns:	The newly created checkbox
		"""
		def parse_title(heading_line):
			# checkbox is not heading
			if REGEX_HEADING.match(heading_line) is not None:
				return None
			m = REGEX_CHECKBOX.match(heading_line)
			if m:
				r = m.groupdict()
				return (len(r[u'level']), r[u'type'], r[u'status'], r[u'title'])

			return None

		if not data:
			raise ValueError(u'Unable to create checkbox, no data provided.')

		# create new checkbox
		nc = cls()
		nc.level, nc.type, nc.status, nc.title = parse_title(data[0])
		nc.body = data[1:]
		if orig_start is not None:
			nc._dirty_heading = False
			nc._dirty_body = False
			nc._orig_start = orig_start
			nc._orig_len = len(nc)
		if heading:
			nc._heading = heading

		return nc

	def update_subtasks(self, total=0, on=0):
		if total != 0:
			percent = (on * 100) / total
		else:
			percent = 0

		count = "%d/%d" % (on, total)
		self.title = REGEX_SUBTASK.sub("[%s]" % (count), self.title)
		self.title = REGEX_SUBTASK_PERCENT.sub("[%d%%]" % (percent), self.title)
		d = self._heading.document.write_checkbox(self, including_children=False)

	@classmethod
	def identify_checkbox(cls, line):
		u""" Test if a certain line is a checkbox or not.

		:line: the line to check

		:returns: indent_level
		"""
		# checkbox is not heading
		if REGEX_HEADING.match(line) is not None:
			return None
		m = REGEX_CHECKBOX.match(line)
		if m:
			r = m.groupdict()
			return len(r[u'level'])

		return None

	@property
	def is_dirty(self):
		u""" Return True if the heading's body is marked dirty """
		return self._dirty_checkbox or self._dirty_body

	@property
	def is_dirty_checkbox(self):
		u""" Return True if the heading is marked dirty """
		return self._dirty_checkbox

	def get_index_in_parent_list(self):
		""" Retrieve the index value of current checkbox in the parents list of
		checkboxes. This works also for top level checkboxes.

		:returns:	Index value or None if heading doesn't have a
					parent/document or is not in the list of checkboxes
		"""
		if self.parent:
			return super(Checkbox, self).get_index_in_parent_list()
		elif self.document:
			l = self.get_parent_list()
			if l:
				return l.index(self)

	def get_parent_list(self):
		""" Retrieve the parents' list of headings. This works also for top
		level headings.

		:returns:	List of headings or None if heading doesn't have a
					parent/document or is not in the list of headings
		"""
		if self.parent:
			return super(Checkbox, self).get_parent_list()
		elif self.document:
			if self in self.document.checkboxes:
				return self.document.checkboxes

	def set_dirty(self):
		u""" Mark the heading and body dirty so that it will be rewritten when
		saving the document """
		self._dirty_checkbox = True
		self._dirty_body = True
		if self._document:
			self._document.set_dirty_document()

	def set_dirty_checkbox(self):
		u""" Mark the checkbox dirty so that it will be rewritten when saving the
		document """
		self._dirty_checkbox = True
		if self._document:
			self._document.set_dirty_document()

	@property
	def previous_checkbox(self):
		u""" Serialized access to the previous checkbox """
		return super(Checkbox, self).previous_item

	@property
	def next_checkbox(self):
		u""" Serialized access to the next checkbox """
		return super(Checkbox, self).next_item

	@property
	def first_checkbox(self):
		u""" Access to the first child heading or None if no children exist """
		if self.children:
			return self.children[0]

	@property
	def start(self):
		u""" Access to the starting line of the checkbox """
		if self.document is None:
			return self._orig_start

		# static computation of start
		if not self.document.is_dirty:
			return self._orig_start

		# dynamic computation of start, really slow!
		def compute_start(h):
			if h:
				return len(h) + compute_start(h.previous_checkbox)
		return compute_start(self.previous_checkbox)

	def toggle(self):
		u""" Toggle status of this checkbox """
		if self.status == Checkbox.STATUS_OFF or self.status is None:
			self.status = Checkbox.STATUS_ON
		else:
			self.status = Checkbox.STATUS_OFF
		self.set_dirty()

	def all_siblings(self):
		if not self.parent:
			p = self._heading
		else:
			p = self.parent
			if not p.children:
				raise StopIteration()

		c = p.first_checkbox
		while c:
			yield c
			c = c.next_sibling
		raise StopIteration()

	def all_children(self):
		if not self.children:
			raise StopIteration()

		c = self.first_checkbox
		while c:
			yield c
			for d in c.all_children():
				yield d
			c = c.next_sibling

		raise StopIteration()

	def all_siblings_status(self):
		u""" Return checkboxes status for currnet checkbox's all siblings

		:return: (total, on)
			total: total # of checkboxes
			on:	   # of checkboxes which are on
		"""
		total, on = 0, 0
		for c in self.all_siblings():
			if c.status is not None:
				total += 1

				if c.status == Checkbox.STATUS_ON:
					on += 1

		return (total, on)

	def are_children_all(self, status):
		u""" Check all children checkboxes status """
		clen = len(self.children)
		for i in range(clen):
			if self.children[i].status != status:
				return False
			# recursively check children's status
			if not self.children[i].are_children_all(status):
				return False

		return True

	def is_child_one(self, status):
		u""" Return true, if there is one child with given status """
		clen = len(self.children)
		for i in range(clen):
			if self.children[i].status == status:
				return True

		return False

	def are_siblings_all(self, status):
		u""" Check all sibling checkboxes status """
		for c in self.all_siblings():
			if c.status != status:
				return False

		return True

	def level():
		u""" Access to the checkbox indent level """
		def fget(self):
			return self._level

		def fset(self, value):
			self._level = int(value)
			self.set_dirty_checkbox()

		def fdel(self):
			self.level = None

		return locals()
	level = property(**level())

	def title():
		u""" Title of current checkbox """
		def fget(self):
			return self._title.strip()

		def fset(self, value):
			if type(value) not in (unicode, str):
				raise ValueError(u'Title must be a string.')
			v = value
			if type(v) == str:
				v = v.decode(u'utf-8')
			self._title = v.strip()
			self.set_dirty_checkbox()

		def fdel(self):
			self.title = u''

		return locals()
	title = property(**title())

	def status():
		u""" status of current checkbox """
		def fget(self):
			return self._status

		def fset(self, value):
			self._status = value
			self.set_dirty()

		def fdel(self):
			self._status = u''

		return locals()
	status = property(**status())

	def type():
		u""" type of current checkbox list type """
		def fget(self):
			return self._type

		def fset(self, value):
			self._type = value

		def fdel(self):
			self._type = u''

		return locals()
	type = property(**type())


class CheckboxList(DomObjList):
	u"""
	Checkbox List
	"""
	def __init__(self, initlist=None, obj=None):
		"""
		:initlist:	Initial data
		:obj:		Link to a concrete Checkbox or Document object
		"""
		# it's not necessary to register a on_change hook because the heading
		# list will itself take care of marking headings dirty or adding
		# headings to the deleted headings list
		DomObjList.__init__(self, initlist, obj)

	@classmethod
	def is_checkbox(cls, obj):
		return CheckboxList.is_domobj(obj)

	def _get_heading(self):
		if self.__class__.is_checkbox(self._obj):
			return self._obj._document
		return self._obj


# vim: set noexpandtab:
