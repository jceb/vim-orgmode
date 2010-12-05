# -*- coding: utf-8 -*-

import vim

import types
import imp
import time

import orgmode.plugins
import orgmode.menu
import orgmode.keybinding
from orgmode.exceptions import PluginError

__all__ = ['echo', 'echom', 'echoe', 'ORGMODE', 'MODE_STAR', 'MODE_INDENT']

def apply_count(f):
	"""
	Decorator which executes function v:count or v:prevount (not implemented, yet) times
	"""
	def r(*args, **kwargs):
		count = 0
		try:
			count = int(vim.eval('v:count'))

			# visual count is not implemented yet
			#if not count:
			#	count = int(vim.eval('v:prevcount'))
		except Exception, e:
			pass

		res = f(*args, **kwargs)
		count -= 1
		while res and count > 0:
			f(*args, **kwargs)
			count -= 1
		return res
	return r

def echo(message):
	"""
	Print a regular message that will not be visible to the user when
	multiple lines are printed
	"""
	print message

def echom(message):
	"""
	Print a regular message that will be visible to the user, even when
	multiple lines are printed
	"""
	# probably some escaping is needed here
	vim.command(':echomsg "%s"' % message)

def echoe(message):
	"""
	Print an error message. This should only be used for serious errors!
	"""
	# probably some escaping is needed here
	vim.command(':echoerr "%s"' % message)

MODE_STAR   = True
MODE_INDENT = False

def indent_orgmode():
	""" Set the indent value for the current line in the variable b:indent_level
	Vim prerequisites:
		:set indentexpr=Method-which-calls-indent_orgmode

	:returns: None
	"""
	from orgmode.heading import Heading, DIRECTION_BACKWARD
	try:
		line = int(vim.eval('v:lnum'))
		heading = Heading.find_heading(line - 1, direction=DIRECTION_BACKWARD)
		if heading and line != heading.start + 1:
			vim.command('let b:indent_level = %d' % (heading.level + 1))
	except Exception, e:
		pass

def fold_orgmode():
	""" Set the fold expression/value for the current line in the variable b:fold_expr
	Vim prerequisites:
		:set foldmethod=expr
		:set foldexpr=Method-which-calls-fold_orgmode

	:returns: None
	"""
	from orgmode.heading import Heading, DIRECTION_BACKWARD
	try:
		line = int(vim.eval('v:lnum'))
		heading = Heading.find_heading(line - 1, direction=DIRECTION_BACKWARD)
		if heading:
			if line == heading.start + 1:
				vim.command('let b:fold_expr = ">%d"' % heading.level)
			elif line == heading.end_of_last_child + 1:
				vim.command('let b:fold_expr = "<%d"' % heading.level)
			else:
				vim.command('let b:fold_expr = %d' % heading.level)
	except Exception, e:
		pass

class OrgMode(object):
	""" Vim Buffer """

	def __init__(self, mode=MODE_STAR):
		object.__init__(self)

		if mode not in (MODE_STAR, MODE_INDENT):
			raise ValueError('Parameter mode is not in (MODE_STAR, MODE_INDENT)')
		self._mode = mode
		self._settings = None
		self.register_menu = True
		self.orgmenu = orgmode.menu.Submenu('&Org')

		self.debug = False

		self._plugins = {}

	@property
	def plugins(self):
		return self._plugins.copy()

	@property
	def mode(self):
		return self._mode

	@orgmode.keybinding.register_keybindings
	@orgmode.menu.register_menu
	def register_plugin(self, plugin):
		if not isinstance(plugin, basestring):
			raise ValueError('Parameter plugin is not of type string')

		if self._plugins.has_key(plugin):
			raise PluginError('Plugin %s has already been loaded')

		# a python module
		module = None

		# actual plugin class
		_class = None

		# locate module and initialize plugin class
		try:
			module = imp.find_module(plugin, orgmode.plugins.__path__)
		except ImportError, e:
			echom('Plugin not found: %s')
			if self.debug:
				raise e
			return

		if not module:
			echom('Plugin not found: %s\n')
			return

		try:
			module = imp.load_module(plugin, *module)
			if not hasattr(module, plugin):
				echoe('Unable to activate plugin: %s' % plugin)
				if self.debug:
					raise PluginError('Unable to find class %s' % plugin)
				return
			_class = getattr(module, plugin)
			self._plugins[plugin] = _class()
			self._plugins[plugin].register()
			if self.debug:
				echo('Plugin registered: %s' % plugin)
			return self._plugins[plugin]
		except Exception, e:
			echoe('Unable to activate plugin: %s' % plugin)
			if self.debug:
				raise e
			return

ORGMODE = OrgMode()

if vim.eval('exists("g:orgmode_plugins")'):
	PLUGINS = vim.eval("g:orgmode_plugins")
	if isinstance(PLUGINS, basestring):
		ORGMODE.register_plugin(PLUGINS)
	elif isinstance(PLUGINS, types.ListType) or \
			isinstance(PLUGINS, types.TupleType):
		for p in PLUGINS:
			ORGMODE.register_plugin(p)
