# -*- coding: utf-8 -*-

import vim

from orgmode.keybinding import Command, Plug, Keybinding
from orgmode.keybinding import MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT

def register_menu(f):
	def r(*args, **kwargs):
		p = f(*args, **kwargs)
		def create(entry):
			if isinstance(entry, Submenu) or isinstance(entry, Separator) \
					or isinstance(entry, ActionEntry):
				entry.create()

		if hasattr(p, u'menu'):
			if isinstance(p.menu, list) or isinstance(p.menu, tuple):
				for e in p.menu:
					create(e)
			else:
				create(p.menu)
		return p
	return r


def add_cmd_mapping_menu(plugin, name, function, key_mapping, menu_desrc):
	u"""A helper function to create a vim command and keybinding and add these
	to the menu for a given plugin.

	:plugin: the plugin to operate on.
	:name: the name of the vim command (and the name of the Plug)
	:function: the actual python function which is called when executing the
				vim command.
	:key_mapping: the keymapping to execute the command.
	:menu_desrc: the text which appears in the menu.
	"""
	cmd = Command(name, function)
	keybinding = Keybinding(key_mapping, Plug(name, cmd))

	plugin.commands.append(cmd)
	plugin.keybindings.append(keybinding)
	plugin.menu + ActionEntry(menu_desrc, keybinding)


class Submenu(object):
	u""" Submenu entry """

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
		n = self.name.replace(u' ', u'\\ ')
		if self.parent:
			return u'%s.%s' % (self.parent.get_menu(), n)
		return n

	def create(self):
		for c in self.children:
			c.create()

	def __str__(self):
		res = self.name
		for c in self.children:
			res += str(c)
		return res

class Separator(object):
	u""" Menu entry for a Separator """

	def __init__(self, parent=None):
		object.__init__(self)
		self.parent = parent

	def __unicode__(self):
		return u'-----'

	def __str__(self):
		return self.__unicode__().encode(u'utf-8')

	def create(self):
		if self.parent:
			menu = self.parent.get_menu()
			vim.command((u'menu %s.-%s- :' % (menu, id(self))).encode(u'utf-8'))

class ActionEntry(object):
	u""" ActionEntry entry """

	def __init__(self, lname, action, rname=None, mode=MODE_NORMAL, parent=None):
		u"""
		:lname: menu title on the left hand side of the menu entry
		:action: could be a vim command sequence or an actual Keybinding
		:rname: menu title that appears on the right hand side of the menu
				entry. If action is a Keybinding this value ignored and is
				taken from the Keybinding
		:mode: defines when the menu entry/action is executable
		:parent: the parent instance of this object. The only valid parent is Submenu
		"""
		object.__init__(self)
		self._lname = lname
		self._action = action
		self._rname = rname
		if mode not in (MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT):
			raise ValueError(u'Parameter mode not in MODE_ALL, MODE_NORMAL, MODE_VISUAL, MODE_INSERT')
		self._mode = mode
		self.parent = parent

	def __str__(self):
		return u'%s\t%s' % (self.lname, self.rname)

	@property
	def lname(self):
		return self._lname.replace(u' ', u'\\ ')

	@property
	def action(self):
		if isinstance(self._action, Keybinding):
			return self._action.action
		return self._action

	@property
	def rname(self):
		if isinstance(self._action, Keybinding):
			return self._action.key.replace(u'<Tab>', u'Tab')
		return self._rname

	@property
	def mode(self):
		if isinstance(self._action, Keybinding):
			return self._action.mode
		return self._mode

	def create(self):
		menucmd = u':%smenu ' % self.mode
		menu = u''
		cmd = u''

		if self.parent:
			menu = self.parent.get_menu()
		menu += u'.%s' % self.lname

		if self.rname:
			cmd = u'%s %s<Tab>%s %s' % (menucmd, menu, self.rname, self.action)
		else:
			cmd = u'%s %s %s' % (menucmd, menu, self.action)

		vim.command(cmd.encode(u'utf-8'))

		# keybindings should be stored in the plugin.keybindings property and be registered by the appropriate keybinding registrar
		#if isinstance(self._action, Keybinding):
		#	self._action.create()


# vim: set noexpandtab:
