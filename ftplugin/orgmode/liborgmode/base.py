# -*- coding: utf-8 -*-

"""
	base
	~~~~~~~~~~

	Here are some really basic data structures that are used throughout
	the liborgmode.
"""

from UserList import UserList


def flatten_list(l):
	"""TODO"""
	res = []
	if type(l) in (tuple, list) or isinstance(l, UserList):
		for i in l:
			if type(i) in (list, tuple) or isinstance(i, UserList):
				res.extend(flatten_list(i))
			else:
				res.append(i)
	return res


class Direction():
	u"""
	Direction is used to indicate the direction of certain actions.

	Example: it defines the direction headings get parted in.
	"""
	FORWARD = 1
	BACKWARD = 2


class MultiPurposeList(UserList):
	u"""
	A Multi Purpose List is a list that calls a user defined hook on
	change. The implementation is very basic - the hook is called without any
	parameters. Otherwise the Multi Purpose List can be used like any other
	list.

	The member element "data" can be used to fill the list without causing the
	list to be marked dirty. This should only be used during initialization!
	"""

	def __init__(self, initlist=None, on_change=None):
		UserList.__init__(self, initlist)
		self._on_change = on_change

	def _changed(self):
		u"""
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

	def __getslice__(self, i, j):
		# fix UserList - don't return a new list of the same type but just the
		# normal list item
		i = max(i, 0)
		j = max(j, 0)
		return self.data[i:j]

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
		UserList.insert(self, i, item)
		self._changed()

	def pop(self, i=-1):
		item = self[i]
		del self[i]
		return item

	def remove(self, item):
		self.__delitem__(self.index(item))

	def reverse(self):
		UserList.reverse(self)
		self._changed()

	def sort(self, *args, **kwds):
		UserList.sort(self, *args, **kwds)
		self._changed()

	def extend(self, other):
		UserList.extend(self, other)
		self._changed()


def get_domobj_range(content=[], position=0, direction=Direction.FORWARD, identify_fun=None):
	u"""
	Get the start and end line number of the dom obj lines from content.

	:content:		String to be recognized dom obj
	:positon:		Line number in content
	:direction:		Search direction
	:identify_fun:  A identify function to recognize dom obj(Heading, Checkbox) title string.

	:return:		Start and end line number for the recognized dom obj.
	"""
	len_cb = len(content)

	if position < 0 or position > len_cb:
		return (None, None)

	tmp_line = position
	start = None
	end = None

	if direction == Direction.FORWARD:
		while tmp_line < len_cb:
			if identify_fun(content[tmp_line]) is not None:
				if start is None:
					start = tmp_line
				elif end is None:
					end = tmp_line - 1
				if start is not None and end is not None:
					break
			tmp_line += 1
	else:
		while tmp_line >= 0 and tmp_line < len_cb:
			if identify_fun(content[tmp_line]) is not None:
				if start is None:
					start = tmp_line
				elif end is None:
					end = tmp_line - 1
				if start is not None and end is not None:
					break
			tmp_line -= 1 if start is None else -1

	return (start, end)

# vim: set noexpandtab:
