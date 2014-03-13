# -*- coding: utf-8 -*-

import vim
from orgmode._vim import echo, echom, echoe, ORGMODE, apply_count, repeat, insert_at_cursor, indent_orgmode
from orgmode.menu import Submenu, Separator, ActionEntry, add_cmd_mapping_menu
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
	def new_checkbox(cls, below=None):
		d = ORGMODE.get_document()
		h = d.current_heading()
		if h is None:
			return
		# init checkboxes for current heading
		h.init_checkboxes()
		c = h.current_checkbox()

		# default checkbox level
		level = h.level
		# if no checkbox is found, insert at current line with indent level=1
		if c is None:
			start = h.start
			if h.checkboxes:
				level = h.first_checkbox.level
		else:
			level = c.level
			if below:
				start = c.end_of_last_child
			else:
				start = c.start

		vim.current.window.cursor = (start + 1, 0)

		if below:
			vim.command("normal o")
		else:
			vim.command("normal O")

		new_checkbox = Checkbox(level=level)
		insert_at_cursor(str(new_checkbox))
		vim.command("call feedkeys('a')")

	@classmethod
	def toggle(cls, checkbox=None):
		u"""
		Toggle the checkbox given in the parameter. 
		If the checkbox is not given, it will toggle the current checkbox.
		"""
		d = ORGMODE.get_document()
		current_heading = d.current_heading()
		# init checkboxes for current heading
		if current_heading is None:
			return
		current_heading = current_heading.init_checkboxes()

		if not checkbox:
			# get current_checkbox
			c = current_heading.current_checkbox()
			# no checkbox found
			if c is None:
				cls.update_checkboxes_status()
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
		d = ORGMODE.get_document()
		h = d.current_heading()
		# init checkboxes for current heading
		h.init_checkboxes()
		# update heading subtask info
		c = h.first_checkbox
		if c is None:
			return
		total, on = c.all_siblings_status()
		h.update_subtasks(total, on)
		# update all checkboxes under current heading 
		cls._update_checkboxes_subtasks(c)
	
	@classmethod
	def _update_checkboxes_subtasks(cls, checkbox):
		# update checkboxes
		for c in checkbox.all_siblings():
			if c.children:
				total, on = c.first_child.all_siblings_status()
				c.update_subtasks(total, on)
				cls._update_checkboxes_subtasks(c.first_child)

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
		add_cmd_mapping_menu(
			self,
			name=u'OrgCheckBoxNewAbove',
			function=u':py ORGMODE.plugins[u"EditCheckbox"].new_checkbox()<CR>',
			key_mapping=u'<localleader>cN',
			menu_desrc=u'New CheckBox Above'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgCheckBoxNewBelow',
			function=u':py ORGMODE.plugins[u"EditCheckbox"].new_checkbox(below=True)<CR>',
			key_mapping=u'<localleader>cn',
			menu_desrc=u'New CheckBox Below'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgCheckBoxToggle',
			function=u':silent! py ORGMODE.plugins[u"EditCheckbox"].toggle()<CR>',
			key_mapping=u'<localleader>cc',
			menu_desrc=u'Toggle Checkbox'
		)
		add_cmd_mapping_menu(
			self,
			name=u'OrgCheckBoxUpdate',
			function=u':silent! py ORGMODE.plugins[u"EditCheckbox"].update_checkboxes_status()<CR>',
			key_mapping=u'<localleader>c#',
			menu_desrc=u'Update Subtasks'
		)

# vim: set noexpandtab:
