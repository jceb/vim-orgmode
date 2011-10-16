# -*- coding: utf-8 -*-

"""
	VIM ORGMODE
	~~~~~~~~~~~~

	TODO
"""

import imp
import types

import vim

import orgmode.keybinding
import orgmode.menu
import orgmode.plugins
import orgmode.settings
from orgmode.exceptions import PluginError
from orgmode.vimbuffer import VimBuffer
from orgmode.liborgmode.agenda import AgendaManager


REPEAT_EXISTS = bool(int(vim.eval('exists("*repeat#set()")')))
TAGSPROPERTIES_EXISTS = False


def realign_tags(f):
	u"""
	Update tag alignment, dependency to TagsProperties plugin!
	"""
	def r(*args, **kwargs):
		global TAGSPROPERTIES_EXISTS
		res = f(*args, **kwargs)

		if not TAGSPROPERTIES_EXISTS and u'TagsProperties' in ORGMODE.plugins:
			TAGSPROPERTIES_EXISTS = True

		if TAGSPROPERTIES_EXISTS:
			ORGMODE.plugins[u'TagsProperties'].realign_tags()

		return res
	return r


def repeat(f):
	u"""
	Integrate with the repeat plugin if available

	The decorated function must return the name of the <Plug> command to
	execute by the repeat plugin.
	"""
	def r(*args, **kwargs):
		res = f(*args, **kwargs)
		if REPEAT_EXISTS and isinstance(res, basestring):
			vim.command((u'silent! call repeat#set("\\<Plug>%s")' % res)
					.encode(u'utf-8'))
		return res
	return r


def apply_count(f):
	u"""
	Decorator which executes function v:count or v:prevount (not implemented,
	yet) times. The decorated function must return a value that evaluates to
	True otherwise the function is not repeated.
	"""
	def r(*args, **kwargs):
		count = 0
		try:
			count = int(vim.eval(u'v:count'.encode('utf-8')))

			# visual count is not implemented yet
			#if not count:
			#	count = int(vim.eval(u'v:prevcount'.encode(u'utf-8')))
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
	u"""
	Print a regular message that will not be visible to the user when
	multiple lines are printed
	"""
	vim.command((u':echo "%s"' % message).encode(u'utf-8'))


def echom(message):
	u"""
	Print a regular message that will be visible to the user, even when
	multiple lines are printed
	"""
	# probably some escaping is needed here
	vim.command((u':echomsg "%s"' % message).encode(u'utf-8'))


def echoe(message):
	u"""
	Print an error message. This should only be used for serious errors!
	"""
	# probably some escaping is needed here
	vim.command((u':echoerr "%s"' % message).encode(u'utf-8'))


def insert_at_cursor(text, move=True, start_insertmode=False):
	u"""Insert text at the position of the cursor.

	If move==True move the cursor with the inserted text.
	"""
	d = ORGMODE.get_document(allow_dirty=True)
	line, col = vim.current.window.cursor
	_text = d._content[line - 1]
	d._content[line - 1] = _text[:col + 1] + text + _text[col + 1:]
	if move:
		vim.current.window.cursor = (line, col + len(text))
	if start_insertmode:
		vim.command(u'startinsert'.encode(u'utf-8'))


def get_user_input(message):
	u"""Print the message and take input from the user.
	Return the input or None if there is no input.
	"""
	vim.command(u'call inputsave()'.encode(u'utf-8'))
	vim.command((u"let user_input = input('" + message + u": ')")
			.encode(u'utf-8'))
	vim.command(u'call inputrestore()'.encode(u'utf-8'))
	try:
		return vim.eval(u'user_input'.encode(u'utf-8')).decode(u'utf-8')
	except:
		return None


def get_bufnumber(bufname):
	"""
	Return the number of the buffer for the given bufname if it exist;
	else None.
	"""
	for b in vim.buffers:
		if b.name == bufname:
			return int(b.number)


def get_bufname(bufnr):
	"""
	Return the name of the buffer for the given bufnr if it exist; else None.
	"""
	for b in vim.buffers:
		if b.number == bufnr:
			return b.name


def indent_orgmode():
	u""" Set the indent value for the current line in the variable
	b:indent_level

	Vim prerequisites:
		:setlocal indentexpr=Method-which-calls-indent_orgmode

	:returns: None
	"""
	line = int(vim.eval(u'v:lnum'.encode(u'utf-8')))
	d = ORGMODE.get_document()
	heading = d.current_heading(line - 1)
	if heading and line != heading.start_vim:
		vim.command((u'let b:indent_level = %d' % (heading.level + 1))
				.encode(u'utf-8'))


def fold_text(allow_dirty=False):
	u""" Set the fold text
		:setlocal foldtext=Method-which-calls-foldtext

	:allow_dirty:	Perform a query without (re)building the DOM if True
	:returns: None
	"""
	line = int(vim.eval(u'v:foldstart'.encode(u'utf-8')))
	d = ORGMODE.get_document(allow_dirty=allow_dirty)
	heading = None
	if allow_dirty:
		heading = d.find_current_heading(line - 1)
	else:
		heading = d.current_heading(line - 1)
	if heading:
		str_heading = unicode(heading)

		# expand tabs
		ts = int(vim.eval(u'&ts'.encode('utf-8')))
		idx = str_heading.find(u'\t')
		if idx != -1:
			tabs, spaces = divmod(idx, ts)
			str_heading = str_heading.replace(u'\t', u' ' * (ts - spaces), 1)
			str_heading = str_heading.replace(u'\t', u' ' * ts)

		# Workaround for vim.command seems to break the completion menu
		vim.eval((u'SetOrgFoldtext("%s")' % (str_heading.replace(
				u'\\', u'\\\\').replace(u'"', u'\\"'), )).encode(u'utf-8'))
		#vim.command((u'let b:foldtext = "%s... "' % \
		#		(str_heading.replace(u'\\', u'\\\\')
		#		.replace(u'"', u'\\"'), )).encode('utf-8'))


def fold_orgmode(allow_dirty=False):
	u""" Set the fold expression/value for the current line in the variable
	b:fold_expr

	Vim prerequisites:
		:setlocal foldmethod=expr
		:setlocal foldexpr=Method-which-calls-fold_orgmode

	:allow_dirty:	Perform a query without (re)building the DOM if True
	:returns: None
	"""
	line = int(vim.eval(u'v:lnum'.encode(u'utf-8')))
	d = ORGMODE.get_document(allow_dirty=allow_dirty)
	heading = None
	if allow_dirty:
		heading = d.find_current_heading(line - 1)
	else:
		heading = d.current_heading(line - 1)
	if heading:
		if line == heading.start_vim:
			vim.command((u'let b:fold_expr = ">%d"' % heading.level).encode(u'utf-8'))
		#elif line == heading.end_vim:
		#	vim.command((u'let b:fold_expr = "<%d"' % heading.level).encode(u'utf-8'))
		# end_of_last_child_vim is a performance junky and is actually not needed
		#elif line == heading.end_of_last_child_vim:
		#	vim.command((u'let b:fold_expr = "<%d"' % heading.level).encode(u'utf-8'))
		else:
			vim.command((u'let b:fold_expr = %d' % heading.level).encode(u'utf-8'))


class OrgMode(object):
	u""" Vim Buffer """

	def __init__(self):
		object.__init__(self)
		self.debug = bool(int(orgmode.settings.get(u'org_debug', False)))

		self.orgmenu = orgmode.menu.Submenu(u'&Org')
		self._plugins = {}
		# list of vim buffer objects
		self._documents = {}

		# agenda manager
		self.agenda_manager = AgendaManager()

	def get_document(self, bufnr=0, allow_dirty=False):
		""" Retrieve instance of vim buffer document. This Document should be
		used for manipulating the vim buffer.

		:bufnr:			Retrieve document with bufnr
		:allow_dirty:	Allow the retrieved document to be dirty

		:returns:	vim buffer instance
		"""
		if bufnr == 0:
			bufnr = vim.current.buffer.number

		if bufnr in self._documents:
			if allow_dirty or self._documents[bufnr].is_insync:
				return self._documents[bufnr]
		self._documents[bufnr] = VimBuffer(bufnr).init_dom()
		return self._documents[bufnr]

	@property
	def plugins(self):
		return self._plugins.copy()

	@orgmode.keybinding.register_keybindings
	@orgmode.keybinding.register_commands
	@orgmode.menu.register_menu
	def register_plugin(self, plugin):
		if not isinstance(plugin, basestring):
			raise ValueError(u'Parameter plugin is not of type string')

		if plugin == u'|':
			self.orgmenu + orgmode.menu.Separator()
			self.orgmenu.children[-1].create()
			return

		if plugin in self._plugins:
			raise PluginError(u'Plugin %s has already been loaded')

		# a python module
		module = None

		# actual plugin class
		_class = None

		# locate module and initialize plugin class
		try:
			module = imp.find_module(plugin, orgmode.plugins.__path__)
		except ImportError, e:
			echom(u'Plugin not found: %s' % plugin)
			if self.debug:
				raise e
			return

		if not module:
			echom(u'Plugin not found: %s' % plugin)
			return

		try:
			module = imp.load_module(plugin, *module)
			if not hasattr(module, plugin):
				echoe(u'Unable to find plugin: %s' % plugin)
				if self.debug:
					raise PluginError(u'Unable to find class %s' % plugin)
				return
			_class = getattr(module, plugin)
			self._plugins[plugin] = _class()
			self._plugins[plugin].register()
			if self.debug:
				echo(u'Plugin registered: %s' % plugin)
			return self._plugins[plugin]
		except Exception, e:
			echoe(u'Unable to activate plugin: %s' % plugin)
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
		vim.command(u'silent! aunmenu Org'.encode(u'utf-8'))

	def start(self):
		u""" Start orgmode and load all requested plugins
		"""
		plugins = orgmode.settings.get(u"org_plugins")

		if not plugins:
			echom(u'orgmode: No plugins registered.')

		if isinstance(plugins, basestring):
			try:
				self.register_plugin(plugins)
			except Exception, e:
				import traceback
				traceback.print_exc()
		elif isinstance(plugins, types.ListType) or \
				isinstance(plugins, types.TupleType):
			for p in plugins:
				try:
					self.register_plugin(p)
				except Exception, e:
					echoe('Error in %s plugin:' % p)
					import traceback
					traceback.print_exc()

		return plugins


ORGMODE = OrgMode()

# vim: set noexpandtab:
