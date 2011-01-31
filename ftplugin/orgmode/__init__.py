# -*- coding: utf-8 -*-

import vim

import types
import imp
import time

import orgmode.plugins
import orgmode.menu
import orgmode.keybinding
import orgmode.settings
from orgmode.exceptions import PluginError

REPEAT_EXISTS = bool(int(vim.eval('exists("*repeat#set()")')))

def repeat(f):
	"""
	Integrate with the repeat plugin if available

	The decorated function must return the name of the <Plug> command to
	execute by the repeat plugin. 
	"""
	def r(*args, **kwargs):
		res = f(*args, **kwargs)
		if REPEAT_EXISTS and isinstance(res, basestring):
			import time
			print res, time.time()
			vim.command('silent! call repeat#set("\\<Plug>%s")' % res)
		return res
	return r

def apply_count(f):
	"""
	Decorator which executes function v:count or v:prevount (not implemented,
	yet) times. The decorated function must return a value that evaluates to
	True otherwise the function is not repeated.
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

def indent_orgmode():
	""" Set the indent value for the current line in the variable b:indent_level
	Vim prerequisites:
		:setlocal indentexpr=Method-which-calls-indent_orgmode

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

def fold_text():
	""" Set the fold text
		:setlocal foldtext=Method-which-calls-foldtext

	:returns: None
	"""
	from orgmode.heading import Heading, DIRECTION_BACKWARD
	try:
		line = int(vim.eval('v:foldstart'))
		heading = Heading.find_heading(line - 1, direction=DIRECTION_BACKWARD)
		if heading:
			str_heading = str(heading)
			ts = int(vim.eval('&ts'))
			idx = str_heading.find('\t')
			if idx != -1:
				tabs, spaces = divmod(idx, ts)

				str_heading = str_heading.replace('\t', ' '*(ts - spaces), 1)
				str_heading = str_heading.replace('\t', ' '*ts)

			vim.command('let b:foldtext = "%s... "' % (str_heading))
	except Exception, e:
		pass

def fold_orgmode():
	""" Set the fold expression/value for the current line in the variable b:fold_expr
	Vim prerequisites:
		:setlocal foldmethod=expr
		:setlocal foldexpr=Method-which-calls-fold_orgmode

	:returns: None
	"""
	from orgmode.heading import Heading, DIRECTION_BACKWARD
	try:
		line = int(vim.eval('v:lnum'))
		heading = Heading.find_heading(line - 1, direction=DIRECTION_BACKWARD)
		if heading:
			if line == heading.start_vim:
				vim.command('let b:fold_expr = ">%d"' % heading.level)
			#elif line == heading.end_vim:
			#	vim.command('let b:fold_expr = "<%d"' % heading.level)
			# end_of_last_child_vim is a performance junky and is actually not needed
			#elif line == heading.end_of_last_child_vim:
			#	vim.command('let b:fold_expr = "<%d"' % heading.level)
			else:
				vim.command('let b:fold_expr = %d' % heading.level)
	except Exception, e:
		pass

class OrgMode(object):
	""" Vim Buffer """

	def __init__(self):
		object.__init__(self)
		self.debug = bool(int(orgmode.settings.get('org_debug', False)))

		self.orgmenu = orgmode.menu.Submenu('&Org')
		self._plugins = {}


	@property
	def plugins(self):
		return self._plugins.copy()

	@orgmode.keybinding.register_keybindings
	@orgmode.menu.register_menu
	def register_plugin(self, plugin):
		if not isinstance(plugin, basestring):
			raise ValueError('Parameter plugin is not of type string')

		if plugin == '|':
			self.orgmenu + orgmode.menu.Separator()
			self.orgmenu.children[-1].create()
			return

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
			echom('Plugin not found: %s' % plugin)
			if self.debug:
				raise e
			return

		if not module:
			echom('Plugin not found: %s' % plugin)
			return

		try:
			module = imp.load_module(plugin, *module)
			if not hasattr(module, plugin):
				echoe('Unable to find plugin: %s' % plugin)
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
				import traceback
				echoe(traceback.format_exc())

	def register_keybindings(self):
		@orgmode.keybinding.register_keybindings
		def dummy(plugin):
			return plugin

		for p in self.plugins.itervalues():
			dummy(p)

	def register_menu(self):
		self.orgmenu.create()

	def unregister_menu(self):
		vim.command('silent! aunmenu Org')

ORGMODE = OrgMode()

PLUGINS = orgmode.settings.get("org_plugins")

if PLUGINS:
	if isinstance(PLUGINS, basestring):
		try:
			ORGMODE.register_plugin(PLUGINS)
		except Exception, e:
			import traceback
			traceback.print_exception()
	elif isinstance(PLUGINS, types.ListType) or \
			isinstance(PLUGINS, types.TupleType):
		for p in PLUGINS:
			try:
				ORGMODE.register_plugin(p)
			except Exception, e:
				import traceback
				traceback.print_exception()
else:
	echoe('orgmode: No plugins registered.')
