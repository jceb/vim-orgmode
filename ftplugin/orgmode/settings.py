# -*- coding: utf-8 -*-

import vim

# for all vim-orgmode buffers
SCOPE_GLOBAL = True

# just for the current buffer - has priority before the global settings
SCOPE_BUFFER = False

VARIABLE_LEADER = {SCOPE_GLOBAL: u'g', SCOPE_BUFFER: u'b'}

u""" Evaluate and store settings """

def get(setting, default=None):
	u""" Evaluate setting in scope of the current buffer,
	globally and also from the contents of the current buffer

	WARNING: Only string values are converted to unicode. If a different value
	is received, e.g. a list or dict, no conversion is done.

	:setting: name of the variable to evaluate
	:default: default value in case the variable is empty

	:returns: variable value
	"""
	# TODO first read setting from org file which take precedence over vim
	# variable settings
	if int(vim.eval((u'exists("b:%s")' % setting).encode(u'utf-8'))):
		res = vim.eval((u"b:%s" % setting).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res

	elif int(vim.eval((u'exists("g:%s")' % setting).encode(u'utf-8'))):
		res = vim.eval((u"g:%s" % setting).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res
	elif default is not None:
		return default

def set(setting, value, scope=SCOPE_GLOBAL, overwrite=False):
	u""" Store setting in the definied scope

	WARNING: For the return value, only string are converted to unicode. If a
	different value is received by vim.eval, e.g. a list or dict, no conversion
	is done.

	:setting: name of the setting
	:value: the actual value, repr is called on the value to create a string representation
	:scope: the scope o the setting/variable
	:overwrite: overwrite existing settings (probably user definied settings)

	:returns: the new value in case of overwrite==False the current value
	"""
	if not overwrite and int(vim.eval((u'exists("%s:%s")' % (VARIABLE_LEADER[scope], setting)).encode(u'utf-8'))):
		res = vim.eval((u'%s:%s' % (VARIABLE_LEADER[scope], setting)).encode(u'utf-8'))
		if type(res) in (unicode, str):
			return res.decode(u'utf-8')
		return res
	v = repr(value)
	if type(value) == unicode:
		# strip leading u of unicode string representations
		v = v[1:]

	vim.command((u'let %s:%s = %s' % (VARIABLE_LEADER[scope], setting, v)).encode(u'utf-8'))
	return value
