# -*- coding: utf-8 -*-


class PluginError(BaseException):
	def __init__(self, message):
		BaseException.__init__(self, message)


class BufferNotFound(BaseException):
	def __init__(self, message):
		BaseException.__init__(self, message)


class BufferNotInSync(BaseException):
	def __init__(self, message):
		BaseException.__init__(self, message)


class HeadingDomError(BaseException):
	def __init__(self, message):
		BaseException.__init__(self, message)

# vim: set noexpandtab:
