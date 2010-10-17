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

class Keybinding(object):
	""" Representation of a single key binding """

	def __init__(self, key, action, mode=MODE_NORMAL, options=None, remap=False, buffer_only=True, silent=True):
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
		return self._action

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
			vim.command(':%smap %s %s %s' % (cmd, ' '.join(self._options), self._key, self._action))
		except Exception, e:
			if ORGMODE.debug:
				echom('Failed to register key binding %s %s' % (self._key, self._action))
