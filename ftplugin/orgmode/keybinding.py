# -*- coding: utf-8 -*-

import vim

MODE_ALL = u'a'
MODE_NORMAL = u'n'
MODE_VISUAL = u'v'
MODE_INSERT = u'i'
MODE_OPERATOR = u'o'

OPTION_BUFFER_ONLY = u'<buffer>'
OPTION_SLIENT = u'<silent>'

def _register(f, name):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		if hasattr(p, name) and isinstance(getattr(p, name), list):
			for i in getattr(p, name):
				i.create()
		return p
	return r

def register_keybindings(f):
	return _register(f, u'keybindings')

def register_commands(f):
	return _register(f, u'commands')

class Command(object):
	u""" A vim command """

	def __init__(self, name, command, arguments=u'0', complete=None, overwrite_exisiting=False):
		u"""
		:name:		The name of command, first character must be uppercase
		:command:	The actual command that is executed
		:arguments:	See :h :command-nargs, only the arguments need to be specified
		:complete:	See :h :command-completion, only the completion arguments need to be specified
		"""
		object.__init__(self)

		self._name                = name
		self._command             = command
		self._arguments           = arguments
		self._complete            = complete
		self._overwrite_exisiting = overwrite_exisiting

	def __unicode__(self):
		return u':%s<CR>' % self.name

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	@property
	def name(self):
		return self._name

	@property
	def command(self):
		return self._command

	@property
	def arguments(self):
		return self._arguments

	@property
	def complete(self):
		return self._complete

	@property
	def overwrite_exisiting(self):
		return self._overwrite_exisiting

	def create(self):
		u""" Register/create the command
		"""
		vim.command((':command%(overwrite)s -nargs=%(arguments)s %(complete)s %(name)s %(command)s' %
				{u'overwrite': '!' if self.overwrite_exisiting else '',
					u'arguments': self.arguments.encode(u'utf-8'),
					u'complete': '-complete=%s' % self.complete.encode(u'utf-8') if self.complete else '',
					u'name': self.name,
					u'command': self.command}
				).encode(u'utf-8'))

class Plug(object):
	u""" Represents a <Plug> to an abitrary command """

	def __init__(self, name, command, mode=MODE_NORMAL):
		u"""
		:name: the name of the <Plug> should be ScriptnameCommandname
		:command: the actual command
		"""
		object.__init__(self)

		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR')
		self._mode = mode

		self.name = name
		self.command = command
		self.created = False

	def __unicode__(self):
		return u'<Plug>%s' % self.name

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def create(self):
		if not self.created:
			self.created = True
			cmd = self._mode
			if cmd == MODE_ALL:
				cmd = u''
			vim.command((u':%snoremap %s %s' % (cmd, str(self), self.command)).encode(u'utf-8'))

	@property
	def mode(self):
		return self._mode

class Keybinding(object):
	u""" Representation of a single key binding """

	def __init__(self, key, action, mode=None, options=None, remap=True, buffer_only=True, silent=True):
		u"""
		:key: the key(s) action is bound to
		:action: the action triggered by key(s)
		:mode: definition in which vim modes the key binding is valid. Should be one of MODE_*
		:option: list of other options like <silent>, <buffer> ...
		:repmap: allow or disallow nested mapping
		:buffer_only: define the key binding only for the current buffer
		"""
		object.__init__(self)
		self._key = key
		self._action = action

		# grab mode from plug if not set otherwise
		if isinstance(self._action, Plug) and not mode:
			mode = self._action.mode

		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT, MODE_OPERATOR')
		self._mode = mode
		self._options = options
		if self._options is None:
			self._options = []
		self._remap = remap
		self._buffer_only = buffer_only
		self._silent = silent

		if self._buffer_only and OPTION_BUFFER_ONLY not in self._options:
			self._options.append(OPTION_BUFFER_ONLY)

		if self._silent and OPTION_SLIENT not in self._options:
			self._options.append(OPTION_SLIENT)

	@property
	def key(self):
		return self._key

	@property
	def action(self):
		return str(self._action)

	@property
	def mode(self):
		return self._mode

	@property
	def options(self):
		return self._options[:]

	@property
	def remap(self):
		return self._remap

	@property
	def buffer_only(self):
		return self._buffer_only

	@property
	def silent(self):
		return self._silent

	def create(self):
		from orgmode import ORGMODE, echom

		cmd = self._mode
		if cmd == MODE_ALL:
			cmd = u''
		if not self._remap:
			cmd += u'nore'
		try:
			create_mapping = True
			if isinstance(self._action, Plug):
				# create plug
				self._action.create()
				if int(vim.eval((u'hasmapto("%s")' % (self._action, )).encode(u'utf-8'))):
					create_mapping = False
			if isinstance(self._action, Command):
				# create command
				self._action.create()

			if create_mapping:
				vim.command((u':%smap %s %s %s' % (cmd, u' '.join(self._options), self._key, self._action)).encode(u'utf-8'))
		except Exception, e:
			if ORGMODE.debug:
				echom(u'Failed to register key binding %s %s' % (self._key, self._action))


# vim: set noexpandtab:
