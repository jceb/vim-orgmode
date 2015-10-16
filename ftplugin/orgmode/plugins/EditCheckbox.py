# -*- coding: utf-8 -*-

import vim
from orgmode._vim import echo, echom, echoe, ORGMODE, apply_count, repeat, insert_at_cursor, indent_orgmode
from orgmode.menu import Submenu, Separator, ActionEntry, add_cmd_mapping_menu
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.liborgmode.checkboxes import Checkbox
from orgmode.liborgmode.dom_obj import OrderListType


class EditCheckbox(object):
	u"""
	Checkbox plugin.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Edit Checkbox')

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

		nc = Checkbox()
		nc._heading = h

		# default checkbox level
		level = h.level + 1
		start = vim.current.window.cursor[0] - 1
		# if no checkbox is found, insert at current line with indent level=1
		if c is None:
			h.checkboxes.append(nc)
		else:
			l = c.get_parent_list()
			idx = c.get_index_in_parent_list()
			if l is not None and idx is not None:
				l.insert(idx + (1 if below else 0), nc)
				# workaround for broken associations, Issue #165
				nc._parent = c.parent
				if below:
					if c.next_sibling:
						c.next_sibling._previous_sibling = nc
					nc._next_sibling = c.next_sibling
					c._next_sibling = nc
					nc._previous_sibling = c
				else:
					if c.previous_sibling:
						c.previous_sibling._next_sibling = nc
					nc._next_sibling = c
					nc._previous_sibling = c.previous_sibling
					c._previous_sibling = nc

			t = c.type
			# increase key for ordered lists
			if t[-1] in OrderListType:
				try:
					num = int(t[:-1]) + (1 if below else -1)
					if num < 0:
						# don't decrease to numbers below zero
						echom(u"Can't decrement further than '0'")
						return
					t = '%d%s' % (num, t[-1])
				except ValueError:
					try:
						char = ord(t[:-1]) + (1 if below else -1)
						if below:
							if char == 91:
								# stop incrementing at Z (90)
								echom(u"Can't increment further than 'Z'")
								return
							elif char == 123:
								# increment from z (122) to A
								char = 65
						else:
							if char == 96:
								# stop decrementing at a (97)
								echom(u"Can't decrement further than 'a'")
								return
							elif char == 64:
								# decrement from A (65) to z
								char = 122
						t = u'%s%s' % (chr(char), t[-1])
					except ValueError:
						pass
			nc.type = t
			if not c.status:
				nc.status = None
			level = c.level

			if below:
				start = c.end_of_last_child
			else:
				start = c.start
		nc.level = level

		if below:
			start += 1
		# vim's buffer behave just opposite to Python's list when inserting a
		# new item.  The new entry is appended in vim put prepended in Python!
		vim.current.buffer[start:start] = [unicode(nc)]

		# update checkboxes status
		cls.update_checkboxes_status()

		vim.command((u'exe "normal %dgg"|startinsert!' % (start + 1, )).encode(u'utf-8'))

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

		if checkbox is None:
			# get current_checkbox
			c = current_heading.current_checkbox()
			# no checkbox found
			if c is None:
				cls.update_checkboxes_status()
				return
		else:
			c = checkbox

		if c.status == Checkbox.STATUS_OFF or c.status is None:
			# set checkbox status on if all children are on
			if not c.children or c.are_children_all(Checkbox.STATUS_ON):
				c.toggle()
				d.write_checkbox(c)
			elif c.status is None:
				c.status = Checkbox.STATUS_OFF
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
		if h is None:
			return
		# init checkboxes for current heading
		h.init_checkboxes()

		cls._update_checkboxes_status(h.first_checkbox)
		cls._update_subtasks()

	@classmethod
	def _update_checkboxes_status(cls, checkbox=None):
		u""" helper function for update checkboxes status
			:checkbox: The first checkbox of this indent level
			:return: The status of the parent checkbox
		"""
		if checkbox is None:
			return

		status_off, status_on, status_int, total = 0, 0, 0, 0
		# update all top level checkboxes' status
		for c in checkbox.all_siblings():
			current_status = c.status
			# if this checkbox is not leaf, its status should determine by all its children
			if c.children:
				current_status = cls._update_checkboxes_status(c.first_child)

			# don't update status if the checkbox has no status
			if c.status is None:
				current_status = None
			# the checkbox needs to have status
			else:
				total += 1

			# count number of status in this checkbox level
			if current_status == Checkbox.STATUS_OFF:
				status_off += 1
			elif current_status == Checkbox.STATUS_ON:
				status_on += 1
			elif current_status == Checkbox.STATUS_INT:
				status_int += 1

			# write status if any update
			if current_status is not None and c.status != current_status:
				c.status = current_status
				d = ORGMODE.get_document()
				d.write_checkbox(c)

		parent_status = Checkbox.STATUS_INT
		# all silbing checkboxes are off status
		if status_off == total:
			parent_status = Checkbox.STATUS_OFF
		# all silbing checkboxes are on status
		elif status_on == total:
			parent_status = Checkbox.STATUS_ON
		# one silbing checkbox is on or int status
		elif status_on != 0 or status_int != 0:
			parent_status = Checkbox.STATUS_INT
		# other cases
		else:
			parent_status = None

		return parent_status

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
