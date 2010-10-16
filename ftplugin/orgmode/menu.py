import vim

MENU_ALL = 'a'
MENU_NORMAL = 'n'
MENU_VISUAL = 'v'
MENU_INSERT = 'i'

def register_menu(f):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		if hasattr(p, 'menu'):
			p.menu.create()
	return r

class SubMenu(object):
	""" SubMenu entry """

	def __init__(self, name, parent=None):
		object.__init__(self)
		self.name = name
		self.parent = parent
		self._children = []

	def __add__(self, entry):
		if entry not in self._children:
			self._children.append(entry)
			entry.parent = self
			return entry

	def __sub__(self, entry):
		if entry in self._children:
			idx = self._children.index(entry)
			del self._children[idx]

	@property
	def children(self):
		return self._children[:]

	def get_menu(self):
		n = self.name.replace(' ', '\\ ')
		if self.parent:
			return '%s.%s' % (self.parent.get_menu(), n)
		return n

	def create(self):
		for c in self.children:
			c.create()

class HorizontalLine(object):
	""" Menu entry for a HorizontalLine """

	def __init__(self, parent):
		object.__init__(self)
		self.parent = parent

	def create(self):
		vim.command('-%s-' % repr(self))

class ActionEntry(object):
	""" ActionEntry entry """

	def __init__(self, rname, action, lname=None, mode=MENU_NORMAL, parent=None):
		object.__init__(self)
		self.rname = rname
		self.action = action
		self.lname = lname
		if mode not in (MENU_ALL, MENU_NORMAL, MENU_VISUAL, MENU_INSERT):
			raise ValueError('Parameter mode not in MENU_ALL, MENU_NORMAL, MENU_VISUAL, MENU_INSERT')
		self.mode = mode
		self.parent = parent

	def create(self):
		menucmd = ':%smenu ' % self.mode
		menu = ''
		cmd = ''

		if self.parent:
			menu = self.parent.get_menu()
		menu += '.%s' % self.rname.replace(' ', '\\ ')

		if self.lname:
			cmd = '%s %s<Tab>%s %s' % (menucmd, menu, self.lname.replace(' ', '\\ '), self.action)
		else:
			cmd = '%s %s %s' % (menucmd, menu, self.action)

		vim.command(cmd)
