# -*- coding: utf-8 -*-

from orgmode import ORGMODE, repeat
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode import settings

import vim

class TagsProperties(object):
	u""" TagsProperties plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&TAGS and Properties')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	@classmethod
	def complete_tags(cls):
		u""" build a list of tags and store it in variable b:org_tag_completion
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			return

		leading_portion = vim.eval(u'a:ArgLead').decode(u'utf-8')
		cursor = int(vim.eval(u'a:CursorPos'))

		# extract currently completed tag
		idx_orig = leading_portion.rfind(u':', 0, cursor)
		if idx_orig == -1:
			idx = 0
		else:
			idx = idx_orig

		current_tag = leading_portion[idx: cursor].lstrip(u':')
		head = leading_portion[:idx + 1]
		if idx_orig == -1:
			head = u''
		tail = leading_portion[cursor:]

		# extract all tags of the current file
		all_tags = set()
		for h in d.all_headings():
			for t in h.tags:
				all_tags.add(t)

		ignorecase = bool(int(settings.get(u'org_tag_completion_ignorecase', int(vim.eval(u'&ignorecase')))))
		possible_tags = []
		current_tags = heading.tags
		for t in all_tags:
			if ignorecase:
				if t.lower().startswith(current_tag.lower()):
					possible_tags.append(t)
			elif t.startswith(current_tag):
				possible_tags.append(t)

		vim.command((u'let b:org_complete_tags = [%s]' % u', '.join([u'"%s%s:%s"' % (head, i, tail) for i in possible_tags])).encode(u'utf-8'))

	@classmethod
	@repeat
	def set_tags(cls):
		u""" Set tags for current heading
		"""
		d = ORGMODE.get_document()
		heading = d.current_heading()
		if not heading:
			return

		# retrieve tags
		res = None
		if heading.tags:
			res = vim.eval(u'input("Tags: ", ":%s:", "customlist,Org_complete_tags")' % u':'.join(heading.tags))
		else:
			res = vim.eval(u'input("Tags: ", "", "customlist,Org_complete_tags")')

		if res is None:
			# user pressed <Esc> abort any further processing
			return

		# remove empty tags
		heading.tags = filter(lambda x: x.strip() != u'', res.decode(u'utf-8').strip().strip(u':').split(u':'))

		d.write()

		return u'OrgSetTags'

	@classmethod
	def realign_tags(cls):
		u"""
		Updates tags when user finished editing a heading
		"""
		d = ORGMODE.get_document(allow_dirty=True)
		heading = d.find_current_heading()
		if not heading:
			return

		if vim.current.window.cursor[0] == heading.start_vim:
			heading.set_dirty_heading()
			d.write_heading(heading, including_children=False)

	@classmethod
	def realign_all_tags(cls):
		u"""
		Updates tags when user finishes editing a heading
		"""
		d = ORGMODE.get_document()
		for heading in d.all_headings():
			heading.set_dirty_heading()

		d.write()

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		settings.set(u'org_tag_column', u'77')

		settings.set(u'org_tag_completion_ignorecase', int(vim.eval(u'&ignorecase')))

		self.keybindings.append(Keybinding(u'<localleader>st', Plug(u'OrgSetTags', u':py ORGMODE.plugins[u"TagsProperties"].set_tags()<CR>')))
		self.menu + ActionEntry(u'Set &Tags', self.keybindings[-1])

		self.commands.append(Command(u'OrgTagsRealign', u":py ORGMODE.plugins[u'TagsProperties'].realign_all_tags()"))

		# workaround to align tags when user is leaving insert mode
		vim.command(u"""function Org_complete_tags(ArgLead, CmdLine, CursorPos)
python << EOF
ORGMODE.plugins[u'TagsProperties'].complete_tags()
EOF
if exists('b:org_complete_tags')
	let tmp = b:org_complete_tags
	unlet b:org_complete_tags
	return tmp
else
	return []
endif
endfunction""".encode(u'utf-8'))

		# this is for all org files opened after this file
		vim.command(u"au orgmode FileType org :au orgmode InsertLeave <buffer> :py ORGMODE.plugins[u'TagsProperties'].realign_tags()".encode(u'utf-8'))

		# this is for the current file
		vim.command(u"au orgmode InsertLeave <buffer> :py ORGMODE.plugins[u'TagsProperties'].realign_tags()".encode(u'utf-8'))
