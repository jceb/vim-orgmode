# -*- coding: utf-8 -*-

import vim
import types

class Heading(object):
	""" Structural heading object """

	def __init__(self, start, end=None, mode=True):
		object.__init__(self)

		self._start = start
		self._end = end

		self._mode = mode
		self._level = Heading.identify_heading(vim.current.buffer[self.start], mode=self._mode)

		if self.level == None:
			raise ValueError('Line number doesn\'t contain a heading!')

		self._parent = None
		self._previous_sibling = None
		self._next_sibling = None
		self._first_child = None
		self._last_child = None

	@property
	def mode(self):
		return self._mode

	@property
	def level(self):
		return self._level

	@property
	def start(self):
		return self._start

	@property
	def end(self):
		if not self._end:
			self._end = Heading.find_heading(self.start, mode=self._mode)
		return self._end

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
				heading = Heading.find_heading(start, mode=self._mode)
				if heading:
					if heading.start == self.start:
						break
					start = heading.start + 1

					# * Heading 1 <- self
					#  * Heading 2 <- first child
					#  * Heading 2 <- anjther child
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
					# * Heading 1 <- sibling
					elif heading.level == self.level:
						if self._next_sibling == None:
							self._next_sibling = heading
							heading._previous_sibling = self
							break

					# * Heading 1
					#  * Heading 2 <- parent
					#    * Heading 4 <- self, the indentation is wrong but someone has to take care of the child
					#   * Heading 3 <- heading
					elif heading.level < self.level and self.parent and \
							self.parent.level < heading.level:
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
					heading = Heading.find_heading(heading.start - 1, False, mode=self._mode)
					if heading.start == self.start:
						break
					if heading:
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

	def previous_sibling():
		def fget(self):
			if self._previous_sibling == None:
				heading = self
				while True:
					heading = Heading.find_heading(heading.start - 1, False, mode=self._mode)
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
							sibling = self
							while sibling:
								if sibling._parent == None:
									sibling._parent = heading
								sibling = sibling.next_sibling
							break
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
	def identify_heading(cls, line, mode=True):
		""" Test if a certain line is a heading or not.

		:line: the line to check
		:mode: if True suppose leading asterisk, if False suppose leading space characters

		:returns: level
		"""
		level = 0
		if not line:
			return None
		if mode:
			for i in xrange(0, len(line)):
				if line[i] == '*':
					level += 1
					if line[i+1] in ('\t', ' '):
						return level
				else:
					return None
		else:
			for i in xrange(0, len(line)):
				if line[i] == ' ':
					level += 1
				elif line[i] == '*':
					level += 1
					if line[i+1] in ('\t', ' '):
						return level
					return None

	@classmethod
	def find_heading(cls, start_line, direction=True, mode=True):
		""" Find heading in the given direction

		:direction: downward == True, upward == False

		:returns: line in buffer or None
		"""
		cb = vim.current.buffer
		len_cb = len(cb)

		if start_line < 0:
			start_line = 0

		if start_line >= len_cb:
			start_line = len_cb - 1

		tmp_line = start_line
		# Search heading upwards
		if direction:
			while tmp_line < len_cb:
				if Heading.identify_heading(cb[tmp_line], mode=mode) != None:
					return Heading(tmp_line, mode=mode)
				tmp_line += 1
		else:
			while tmp_line >= 0:
				if Heading.identify_heading(cb[tmp_line], mode=mode) != None:
					return Heading(tmp_line, mode=mode)
				tmp_line -= 1

	@classmethod
	def current_heading(cls, mode=True):
		""" Find the current heading and return the related object

		:returns: Heading object or None
		"""
		heading = Heading.find_heading(vim.current.window.cursor[0] - 1, False, mode)
		if heading != None:
			return heading

class OrgMode(object):
	""" Vim Buffer """

	def __init__(self, mode=True):
		""" TODO: Fill me in

		:text: TODO
		"""
		object.__init__(self)

		self._mode = mode

	@property
	def mode(self):
		return self._mode

	def unregister_plugin(self, plugin):
		pass

	def register_plugin(self, plugin):
		print 'register plugin %s' % plugin

	def unregister_menu(self):
		pass

	def register_menu(self):
		pass

	def unregister_keybinding(self):
		pass

	def register_keybinding(self):
		pass

	def find_current_heading(self, mode=True):
		""" TODO: Docstring for find_current_heading

		:returns: TODO
		"""
		heading = Heading.current_heading(mode)
		if heading:
			if heading.parent:
				print 'parent', vim.current.buffer[heading.parent.start]
			print heading.level, heading.start, vim.current.buffer[heading.start]
			print 'children', len(heading.children)
			if heading.previous_sibling:
				print 'previous sibling', vim.current.buffer[heading.previous_sibling.start]
			if heading.next_sibling:
				print 'next sibling', vim.current.buffer[heading.next_sibling.start]
		else:
			print 'nothing found'

ORGMODE = OrgMode()

if vim.eval('exists("g:orgmode_plugins")'):
	PLUGINS = vim.eval("g:orgmode_plugins")
	if isinstance(PLUGINS, basestring):
		ORGMODE.register_plugin(PLUGINS)
	elif isinstance(PLUGINS, types.ListType) or \
			isinstance(PLUGINS, types.TupleType):
				for p in PLUGINS:
					ORGMODE.register_plugin(p)
