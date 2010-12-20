# -*- coding: utf-8 -*-

import vim

MODE_ALL = 'a'
MODE_NORMAL = 'n'
MODE_VISUAL = 'v'
MODE_INSERT = 'i'

OPTION_BUFFER_ONLY = '<buffer>'
OPTION_SLIENT = '<silent>'

def register_keybindings(f):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		if hasattr(p, 'keybindings') and isinstance(p.keybindings, list):
			for k in p.keybindings:
				k.create()
		return p
	return r

class Plug(object):
	""" Represents a <Plug> to an abitrary command """

	def __init__(self, name, command, mode=MODE_NORMAL):
		"""
		:name: the name of the <Plug> should be ScriptnameCommandname
		:command: the actual command
		"""
		object.__init__(self)

		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT):
			raise ValueError('Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT')
		self._mode = mode

		self.name = name
		self.command = command
		self.created = False

	def __str__(self):
		return '<Plug>%s' % self.name

	def create(self):
		if not self.created:
			self.created = True
			cmd = self._mode
			if cmd == MODE_ALL:
				cmd = ''
			vim.command(':%snoremap %s %s' % (cmd, str(self), self.command))

class Keybinding(object):
	""" Representation of a single key binding """

	def __init__(self, key, action, mode=MODE_NORMAL, options=None, remap=True, buffer_only=True, silent=True):
		"""
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
		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT):
			raise ValueError('Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT')
		self._mode = mode
		self._options = options
		if self._options == None:
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
			cmd = ''
		if not self._remap:
			cmd += 'nore'
		try:
			if isinstance(self._action, Plug):
				self._action.create()
				if not int(vim.eval('hasmapto("%s")' % (self._action, ))):
					vim.command(':%smap %s %s %s' % (cmd, ' '.join(self._options), self._key, self._action))
			else:
				vim.command(':%smap %s %s %s' % (cmd, ' '.join(self._options), self._key, self._action))
		except Exception, e:
			if ORGMODE.debug:
				echom('Failed to register key binding %s %s' % (self._key, self._action))
