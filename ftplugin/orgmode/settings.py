# -*- coding: utf-8 -*-

import vim

# for all vim-orgmode buffers
SCOPE_GLOBAL = True

# just for the current buffer - has priority before the global settings
SCOPE_BUFFER = False

VARIABLE_LEADER = {SCOPE_GLOBAL: 'g', SCOPE_BUFFER: 'b'}

""" Evaluate and store settings """

def get(setting, default=None):
	""" Evaluate setting in scope of the current buffer, 
	globally and also from the contents of the current buffer
	
	:setting: name of the variable to evaluate
	:default: default value in case the variable is empty

	:returns: variable value
	"""
	# TODO first read setting from file
	if int(vim.eval('exists("b:%s")' % setting)):
		return vim.eval("b:%s" % setting)
	elif int(vim.eval('exists("g:%s")' % setting)):
		return vim.eval("g:%s" % setting)
	elif default != None:
		return default

def set(setting, value, scope=SCOPE_GLOBAL, overwrite=False):
	""" Store setting in the definied scope
	
	:setting: name of the setting
	:value: the actual value, repr is called on the value to create a string representation
	:scope: the scope o the setting/variable
	:overwrite: overwrite existing settings (probably user definied settings)

	:returns: the new value in case of overwrite==False the current value
	"""
	if not overwrite and int(vim.eval('exists("%s:%s")' % (VARIABLE_LEADER[scope], setting))):
		return vim.eval('%s:%s' % (VARIABLE_LEADER[scope], setting))
	vim.command('let %s:%s = %s' % (VARIABLE_LEADER[scope], setting, repr(value)))
	return value
