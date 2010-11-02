# -*- coding: utf-8 -*-

class VimWindow(object):
	""" Docstring for VimWindow """

	def __init__(self, buf):
		""" TODO: Fill me in """
		object.__init__(self)
		self.buffer = buf
		self.cursor = (1, 0)

class VimTest(object):
	""" Replacement for vim API """

	def __init__(self):
		object.__init__(self)
		self.buffer = ""
		self.window = VimWindow(self)

EVALRESULTS = {}

def eval(cmd):
	""" evaluate command

	:returns: TODO
	"""
	return EVALRESULTS.get(cmd, None)

CMDHISTORY = []
CMDRESULTS = {}
def command(cmd):
	CMDHISTORY.append(cmd)
	return CMDRESULTS.get(cmd, None)

current = VimTest()
