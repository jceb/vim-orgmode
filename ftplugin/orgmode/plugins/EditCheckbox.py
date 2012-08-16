# -*- coding: utf-8 -*-

from orgmode._vim import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.liborgmode.checkboxes import Checkbox


class EditCheckbox(object):
	u"""
	Checkbox plugin.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'EditCheckbox')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def toggle(cls, checkbox=None):
		u"""
		Toggle the checkbox given in the parameter. 
		If the checkbox is not given, it will toggle the current checkbox.
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		# init checkboxes for current heading
		current_heading = current_heading.init_checkboxes()

		if not checkbox:
			# get current_checkbox
			c = current_heading.current_checkbox()
			# no checkbox found
			if c is None:
				return
		else:
			c = checkbox

		if c.status == Checkbox.STATUS_OFF:
			# set checkbox status on if all children are on
			if not c.children or c.are_children_all(Checkbox.STATUS_ON):
				c.toggle()
				d.write_checkbox(c)

		elif c.status == Checkbox.STATUS_ON:
			if not c.children or c.is_child_one(Checkbox.STATUS_OFF):
				c.toggle()
				d.write_checkbox(c)

		elif c.status == Checkbox.STATUS_INT:
			# can't toggle intermediate state directly according to emacs orgmode
			pass
		# update checkboxes status
		cls.update_checkboxes_status()

	@classmethod
	def _update_subtasks(cls):
		u""" """
		d = ORGMODE.get_document()
		h = d.current_heading()
		# init checkboxes for current heading
		h.init_checkboxes()
		# update heading subtask info
		c = h.first_checkbox
		# print c
		on, total = c.all_siblings_status()
		# update buffer
		h.update_subtasks(total, on)

	@classmethod
	def update_checkboxes_status(cls):
		d = ORGMODE.get_document()
		h = d.current_heading()
		# init checkboxes for current heading
		h.init_checkboxes()

		cls._update_checkboxes_status(h.first_checkbox)
		cls._update_subtasks()
	
	@classmethod
	def _update_checkboxes_status(cls, checkbox=None):
		u""" helper function for update checkboxes status """
		if not checkbox:
			return

		# update all top level checkboxes' status
		for c in checkbox.all_siblings():
			cls._update_status(c)

	@classmethod
	def _update_status(cls, c):
		status = c.status
		d = ORGMODE.get_document()
		if status == Checkbox.STATUS_OFF:
			if c.children:
				if c.are_children_all(Checkbox.STATUS_ON):
					c.status = Checkbox.STATUS_ON
					d.write_checkbox(c)
					# check if the parent need to be set on
					if c.parent:
						cls._update_status(c.parent)
				else:
					if c.is_child_one(Checkbox.STATUS_ON):
						c.status = Checkbox.STATUS_INT
						d.write_checkbox(c)
					if c.children:
						cls._update_checkboxes_status(c.first_child)

		elif status == Checkbox.STATUS_ON:
			# since all children are on, we don't need to check children recursively
			if c.are_children_all(status):
				return
			else:
				if c.is_child_one(Checkbox.STATUS_ON):
					c.status = Checkbox.STATUS_INT
					d.write_checkbox(c)
				else:
					c.status = Checkbox.STATUS_OFF
					d.write_checkbox(c)

				if c.parent:
					cls._update_status(c.parent)

				if c.children:
					d.write_checkbox(c)
					cls._update_checkboxes_status(c.first_child)

		elif status == Checkbox.STATUS_INT:
			# children are all on 
			if c.are_children_all(Checkbox.STATUS_ON):
				c.status = Checkbox.STATUS_ON
				d.write_checkbox(c)
				if c.parent:
					cls._update_status(c.parent)
			# children are all off
			elif not c.is_child_one(Checkbox.STATUS_ON):
				c.status = Checkbox.STATUS_OFF
				d.write_checkbox(c)
				if c.parent:
					cls._update_status(c.parent)
					
			if c.children:
				cls._update_checkboxes_status(c.first_child)

	def register(self):
		u"""
		Registration of the plugin.

		Key bindings and other initialization should be done here.
		"""
		self.keybindings.append(Keybinding(u'<localleader>cc',
				# Plug(u'OrgEditCheckboxToggle', u':silent! py ORGMODE.plugins[u"EditCheckbox"].toggle()<CR>')))
				Plug(u'OrgEditCheckboxToggle', u':py ORGMODE.plugins[u"EditCheckbox"].toggle()<CR>')))
		self.menu + ActionEntry(u'Toggle Checkbox', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>c#',
				# Plug(u'OrgEditCheckboxUpdateSubtasks', u':silent! py ORGMODE.plugins[u"EditCheckbox"].update_checkboxes_status()<CR>')))
				Plug(u'OrgEditCheckboxUpdateSubtasks', u':py ORGMODE.plugins[u"EditCheckbox"].update_checkboxes_status()<CR>')))
		self.menu + ActionEntry(u'Update Subtasks', self.keybindings[-1])

# vim: set noexpandtab:
