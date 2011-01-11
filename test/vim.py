# -*- coding: utf-8 -*-

class VimWindow(object):
	""" Docstring for VimWindow """

	def __init__(self, test):
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
EVALRESULTS = {
		'exists("g:org_debug")': 0,
		'exists("b:org_debug")': 0,
		'exists("*repeat#set()")': 0,
		'exists("b:org_plugins")': 0,
		'exists("g:org_plugins")': 0,
		}

def eval(cmd):
	""" evaluate command

	:returns: results stored in EVALRESULTS
	"""
	EVALHISTORY.append(cmd)
	return EVALRESULTS.get(cmd, None)

CMDHISTORY = []
CMDRESULTS = {}
def command(cmd):
	CMDHISTORY.append(cmd)
	return CMDRESULTS.get(cmd, None)

current = VimTest()
