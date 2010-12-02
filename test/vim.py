# -*- coding: utf-8 -*-

class VimWindow(object):
	""" Docstring for VimWindow """

	def __init__(self, test):
		""" TODO: Fill me in """
		object.__init__(self)
		self._test = test
		self.cursor = (1, 0)
	
	def buffer():
		def fget(self):
			return self._test.buffer
		def fset(self, value):
			self._test.buffer = value
		return locals()
	buffer = property(**buffer())

class VimBuffer(list):
	def __init__(self, iterable=None):
		if iterable != None:
			list.__init__(self, iterable)
		else:
			list.__init__(self)
	
	def append(self, o):
		"""
		mimic the specific behavior of vim.current.buffer
		"""
		if isinstance(o, list) or isinstance(o, tuple):
			for i in o:
				list.append(self, i)
		else:
			list.append(self, o)

class VimTest(object):
	""" Replacement for vim API """

	def __init__(self):
		object.__init__(self)
		self._buffer = VimBuffer()
		self.window = VimWindow(self)
	
	def buffer():
		def fget(self):
			return self._buffer
		def fset(self, value):
			self._buffer = VimBuffer(value)
		return locals()
	buffer = property(**buffer())

EVALHISTORY = []
EVALRESULTS = {}

def eval(cmd):
	""" evaluate command

	:returns: TODO
	"""
	EVALHISTORY.append(cmd)
	return EVALRESULTS.get(cmd, None)

CMDHISTORY = []
CMDRESULTS = {}
def command(cmd):
	CMDHISTORY.append(cmd)
	return CMDRESULTS.get(cmd, None)

current = VimTest()
