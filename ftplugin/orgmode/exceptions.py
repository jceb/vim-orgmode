# -*- coding: utf-8 -*-

class PluginError(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)
