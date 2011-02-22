# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
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
			text = self.text.decode('utf-8')
			idx = text.rfind(' ')
			idx2 = text.rfind('\t')
			idx = idx if idx > idx2 else idx2

			if not value:
				if self.tags:
					# remove tags
					vim.current.buffer[self.start] = '%s %s' % ('*'*self.level, text[:idx].strip().encode('utf-8'))
			else:
				if self.tags:
					text = text[:idx]
				text = text.strip()

				tabs = 0
				spaces = 2
				tags = ':%s:' % (':'.join(value))

				tag_column = int(settings.get('org_tags_column', '77'))

				len_heading = self.level + 1 + len(text)
				if len_heading + spaces + len(tags) < tag_column:
					ts = int(vim.eval('&ts'))
					tmp_spaces =  ts - divmod(len_heading, ts)[1]

					if len_heading + tmp_spaces + len(tags) < tag_column:
						tabs, spaces = divmod(tag_column - (len_heading + tmp_spaces + len(tags)), ts)

						if tmp_spaces:
							tabs += 1
					else:
						spaces = tag_column - (len_heading + len(tags))

				# add tags
				vim.current.buffer[self.start] = '%s %s%s%s%s' % ('*'*self.level, text.encode('utf-8'), '\t'*tabs, ' '*spaces, tags)

			self._tags = value
		return locals()
	tags = property(**tags())

	@classmethod
	def complete_tags(cls):
		""" build a list of tags and store it in variable b:org_tag_completion
		"""
		heading = cls.current_heading()
		if not heading:
			return

		leading_portion = vim.eval('a:ArgLead')
		cursor = int(vim.eval('a:CursorPos'))

		# extract currently completed tag
		idx_orig = leading_portion.rfind(':', 0, cursor)
		if idx_orig == -1:
			idx = 0
		else:
			idx = idx_orig

		current_tag = leading_portion[idx: cursor].lstrip(':')
		head = leading_portion[:idx + 1]
		if idx_orig == -1:
			head = ''
		tail = leading_portion[cursor:]

		# extract all tags of the current file
		all_tags = set()
		for h in cls.all_headings():
			for t in h.tags:
				all_tags.add(t)

		ignorecase = bool(int(settings.get('org_tags_completion_ignorecase', '0')))
		possible_tags = []
		for t in all_tags:
			if ignorecase:
				if t.lower().startswith(current_tag.lower()):
					possible_tags.append(t)
			elif t.startswith(current_tag):
				possible_tags.append(t)

		vim.command('let b:org_complete_tags = [%s]' % ', '.join(['"%s%s:%s"' % (head, i, tail) for i in possible_tags]))

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

		# commands for this plugin
		self.commands = []

	@repeat
	def set_tags(self):
		""" Set tags for current heading
		"""
		heading = HeadingTags.current_heading()
		if not heading:
			return

		# retrieve tags
		res = None
		if heading.tags:
			res = vim.eval('input("Tags: ", ":%s:", "customlist,Org_complete_tags")' % ':'.join(heading.tags))
		else:
			res = vim.eval('input("Tags: ", "", "customlist,Org_complete_tags")')

		if res == None:
			# user pressed <Esc> abort any further processing
			return

		# remove empty tags
		heading.tags = filter(lambda x: x.strip() != '', res.strip().strip(':').split(':'))

		return 'OrgSetTags'

	def update_tags(self):
		"""
		Updates tags when user finishes editing a heading
		"""
		heading = HeadingTags.current_heading()
		if not heading:
			return

		if vim.current.window.cursor[0] == heading.start_vim:
			heading.tags = heading.tags

	def realign_tags(self):
		"""
		Updates tags when user finishes editing a heading
		"""
		for h in HeadingTags.all_headings():
			if h.tags:
				h.tags = h.tags

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		settings.set('org_tags_column', '77')

		settings.set('org_tags_completion_ignorecase', '0')

		settings.set('org_leader', ',')
		leader = settings.get('org_leader', ',')

		self.keybindings.append(Keybinding('%st' % leader, Plug('OrgSetTags', ':py ORGMODE.plugins["TagsProperties"].set_tags()<CR>')))
		self.menu + ActionEntry('Set &Tags', self.keybindings[-1])

		self.commands.append(Command('OrgTagsRealign', ":py ORGMODE.plugins['TagsProperties'].realign_tags()"))

		# workaround to align tags when user is leaving insert mode
		vim.command("""function Org_complete_tags(ArgLead, CmdLine, CursorPos)
python << EOF
from orgmode.plugins.TagsProperties import HeadingTags
HeadingTags.complete_tags()
EOF
if exists('b:org_complete_tags')
	let tmp = b:org_complete_tags
	unlet b:org_complete_tags
	return tmp
else
	return []
endif
endfunction""")

		# this is for all org files opened after this file
		vim.command("au FileType org :au InsertLeave <buffer> :silent! py ORGMODE.plugins['TagsProperties'].update_tags()")

		# this is for the current file
		vim.command("au InsertLeave <buffer> :silent! py ORGMODE.plugins['TagsProperties'].update_tags()")
