# -*- coding: utf-8 -*-

import vim

DIRECTION_FORWARD  = True
DIRECTION_BACKWARD = False

class Heading(object):
	""" Structural heading object """

	def __init__(self, start):
		object.__init__(self)

		self._start = start
		self._end = None

		self._level = Heading.identify_heading(vim.current.buffer[self.start])

		if self.level == None:
			raise ValueError('Line number doesn\'t contain a heading!')

		self._parent = None
		self._previous_sibling = None
		self._next_sibling = None
		self._first_child = None
		self._last_child = None

	def __str__(self):
		return vim.current.buffer[self.start]

	@property
	def text(self):
		""" Return the text of the current heading, all surrounding strings are stripped
		"""
		return vim.current.buffer[self.start][self.level + 1:]

	@property
	def level(self):
		return self._level

	@property
	def start(self):
		return self._start

	@property
	def start_vim(self):
		return self.start + 1

	@property
	def end(self):
		if not self._end:
			tmp = len(vim.current.buffer) - 1
			if self.children:
				tmp = self.children[0].start - 1
			elif self.next_sibling:
				tmp = self.next_sibling.start - 1
			else:
				p = self.parent
				while p:
					if p.next_sibling:
						tmp = p.next_sibling.start - 1
						break
					p = p.parent
			self._end = tmp
		return self._end

	@property
	def end_vim(self):
		return self.end + 1

	@property
	def end_of_last_child(self):
		if self.has_children():
			child = self.children[-1]
			while child.has_children():
				child = child.children[-1]
			return child.end
		return self.end

	@property
	def end_of_last_child_vim(self):
		return self.end_of_last_child + 1

	def has_children(self):
		if self._first_child == None:
			for i in self.iterchildren():
				break
		if self._first_child != None:
			return True
		return False

	@property
	def children(self):
		tmp = []
		for c in self.iterchildren():
			tmp.append(c)
		return tmp

	#def first_child():
	#	"""The RW property first_child"""
	#	def fget(self):
	#		return self._first_child
	#	def fset(self, value):
	#		self._first_child = value
	#	return locals()
	#first_child = property(**first_child())

	#def last_child():
	#	"""The RW property last_child"""
	#	def fget(self):
	#		return self._last_child
	#	def fset(self, value):
	#		self._last_child = value
	#	return locals()
	#last_child = property(**last_child())

	def iterchildren(self):
		if self._first_child == None:
			last_child = None
			start = self._end
			if start == None:
				start = self.start + 1
			while True:
				heading = Heading.find_heading(start)
				if heading:
					if heading.start == self.start:
						break
					start = heading.start + 1

					# * Heading 1 <- self
					#  * Heading 2 <- first child
					#  * Heading 2 <- another child
					if heading.level == self.level + 1:
						if self._first_child == None:
							self._first_child = heading
						heading._parent = self
						if last_child and not heading._previous_sibling:
							heading._previous_sibling = last_child
						if last_child and not last_child._next_sibling:
							last_child._next_sibling = heading
						yield heading
						if heading.has_children():
							# skip children
							start = heading.children[-1].start + 1

					# * Heading 1 <- self
					# * Heading 2 <- sibling
					elif heading.level == self.level:
						if self._next_sibling == None:
							self._next_sibling = heading
							heading._previous_sibling = self
						break

					# * Heading 1
					#  * Heading 2 <- parent
					#    * Heading 4 <- self, the indentation is wrong but someone has to take care of the child
					#   * Heading 3 <- heading
					elif heading.level < self.level and ((self.parent and \
							self.parent.level < heading.level) or \
							not self.parent):
						if self._next_sibling == None:
							self._next_sibling = heading
							heading._previous_sibling = self
						break

					# * Heading 1
					#  * Heading 2 <- self
					#    * Heading 4 <- child, the indentation is wrong but someone has to take care of the child
					#   * Heading 3 <- another child
					elif heading.level > self.level:
						if not self._first_child:
							self._first_child = heading
							heading._parent = self
							yield heading
							if heading.has_children():
								# skip children
								start = heading.children[-1].start + 1
					else:
						break
					last_child = heading
				else:
					break
			raise StopIteration()
		else:
			child = self._first_child
			while child:
				yield child
				child = child.next_sibling
			raise StopIteration()

	def parent():
		def fget(self):
			if self.level != 1 and self._parent == None:
				heading = self
				previous = self.previous_sibling
				while previous:
					heading = previous
					previous = heading.previous_sibling
				while True:
					heading = Heading.find_heading(heading.start - 1, DIRECTION_BACKWARD)
					if heading:
						if heading.start == self.start:
							break
						if heading.level < self.level:
							self._parent = heading
							sibling = previous
							while sibling:
								if sibling.parent == None:
									sibling.parent = heading
								if not sibling.next_sibling:
									heading.last_child = sibling
								sibling = sibling.next_sibling
							break
					else:
						break
			return self._parent

		def fset(self, parent):
			raise 'not implemented'
			self._parent = parent

		return locals()
	parent = property(**parent())

	@property
	def number_of_parents(self):
		def count_parents(h):
			if h.parent:
				return 1 + count_parents(h.parent)
			else:
				return 0
		return count_parents(self)

	def previous_sibling():
		def fget(self):
			if self._previous_sibling == None:
				heading = self
				tmp_heading = None
				while True:
					heading = Heading.find_heading(heading.start - 1, DIRECTION_BACKWARD)
					if heading:
						if heading.start == self.start:
							break
						if heading.level == self.level:
							self._previous_sibling = heading
							heading._next_sibling = self
							break
						elif heading.level < self.level:
							if self._parent == None:
								self._parent = heading
							if tmp_heading:
								self._previous_sibling = tmp_heading
								tmp_heading._parent = heading
								tmp_heading._next_sibling = self
								tmp_heading = None
							sibling = self
							while sibling:
								if sibling._parent == None:
									sibling._parent = heading
								sibling = sibling.next_sibling
							break
						else:
							# save previous heading, it might have a wrong
							# level but still is a sibling
							tmp_heading = heading
					else:
						break
			return self._previous_sibling

		def fset(self, previous_sibling):
			raise 'not implemented'
			self._previous_sibling = previous_sibling

		return locals()
	previous_sibling = property(**previous_sibling())

	def next_sibling():
		def fget(self):
			if self._next_sibling == None:
				# this will set next_sibling if exists
				for c in self.iterchildren():
					pass
			return self._next_sibling

		def fset(self, next_sibling):
			raise 'not implemented'
			self._next_sibling = next_sibling

		return locals()
	next_sibling = property(**next_sibling())

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

	@classmethod
	def find_heading(cls, start_line, direction=DIRECTION_FORWARD):
		""" Find heading in the given direction

		:start_line: start line, counting from 0
		:direction: downward == DIRECTION_FORWARD, upward == DIRECTION_BACKWARD

		:returns: Heading object or None
		"""
		cb = vim.current.buffer
		len_cb = len(cb)

		if start_line < 0:
			start_line = 0

		if start_line >= len_cb:
			start_line = len_cb - 1

		tmp_line = start_line
		# Search heading upwards
		if direction == DIRECTION_FORWARD:
			while tmp_line < len_cb:
				if cls.identify_heading(cb[tmp_line]) != None:
					return cls(tmp_line)
				tmp_line += 1
		else:
			while tmp_line >= 0:
				if cls.identify_heading(cb[tmp_line]) != None:
					return cls(tmp_line)
				tmp_line -= 1

	@classmethod
	def current_heading(cls):
		""" Find the current heading (search backward) and return the related object

		:returns: Heading object or None
		"""
		return cls.find_heading(vim.current.window.cursor[0] - 1, DIRECTION_BACKWARD)

	@classmethod
	def next_heading(cls):
		""" Find the next heading (search forward) and return the related object

		:returns: Heading object or None
		"""
		return cls.find_heading(vim.current.window.cursor[0] - 1, DIRECTION_FORWARD)

	@classmethod
	def previous_heading(cls):
		""" Find the next heading (search forward) and return the related object

		:returns: Heading object or None
		"""
		h = cls.current_heading()
		if h:
			return cls.find_heading(h.start - 1, DIRECTION_BACKWARD)

	@classmethod
	def all_headings(cls):
		""" Returns an iterator object which returns all headings of the
		current file
		"""
		h = cls.find_heading(0, DIRECTION_FORWARD)
		while h:
			yield h
			h = cls.find_heading(h.start + 1, DIRECTION_FORWARD)
