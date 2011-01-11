# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD
from orgmode import settings

import vim

class HeadingTags(Heading):
	""" Heading with Tags functionality """

	def __init__(self, *args, **kwargs):
		Heading.__init__(self, *args, **kwargs)
		self._tags = None
	
	def tags():
		""" Tags """
		def fget(self):
			if self._tags == None:
				text = self.text.split()
				if not text or len(text[-1]) <= 2 or text[-1][0] != ':' or text[-1][-1] != ':':
					self._tags = []
				else:
					self._tags = [ x for x in text[-1].split(':') if x ]
			return self._tags

		def fset(self, value):
			"""
			:value:	list of tags, the empty list deletes all tags
			"""
			# find beginning of tags
			idx = self.text.rfind(' ')
			idx2 = self.text.rfind('\t')
			idx = idx if idx > idx2 else idx2

			if not value:
				if self.tags:
					# remove tags
					vim.current.buffer[self.start] = '%s %s' % ('*'*self.level, self.text[:idx].strip())
			else:
				text = self.text.strip()
				if self.tags:
					text = text[:idx].strip()

				tabs = 0
				spaces = 2
				tags = ':%s:' % (':'.join(value))

				tag_column = int(settings.get('org_tags_column', '78'))
				
				if self.level + 1 + len(text) + spaces + len(tags) < tag_column:
					tabs, spaces = divmod(tag_column - (self.level + 1 + len(text) + len(tags)),
							int(vim.eval('&sw')))

				# add tags
				vim.current.buffer[self.start] = '%s %s%s%s%s' % ('*'*self.level, text, '\t'*tabs, ' '*spaces, tags)

			self._tags = value
		return locals()
	tags = property(**tags())

class TagsProperties(object):
	""" TagsProperties plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('&TAGS and Properties')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@repeat
	def set_tags(self):
		""" Set tags for current heading
		"""
		heading = HeadingTags.current_heading()
		if not heading:
			return

		# retrieve tags
		tags = vim.eval('input("Tags: ", ":%s:")' % ':'.join(heading.tags)).strip().strip(':').split(':')
		heading.tags = tags

		return 'OrgSetTags'

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		settings.set('org_tags_column', '78')

		settings.set('org_tags_properties_leader', ',')
		leader = settings.get('org_tags_properties_leader', ',')

		self.keybindings.append(Keybinding('%st' % leader, Plug('OrgSetTags', ':py ORGMODE.plugins["TagsProperties"].set_tags()<CR>')))
		self.menu + ActionEntry('Set &Tags', self.keybindings[-1])
