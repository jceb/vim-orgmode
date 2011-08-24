# -*- coding: utf-8 -*-

class PluginError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class BufferNotFound(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class BufferNotInSync(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class HeadingDomError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

# vim: set noexpandtab:
