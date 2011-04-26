# -*- coding: utf-8 -*-

from orgmode import ORGMODE, repeat
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.liborgmode import Document
from orgmode import settings

import vim

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

	@classmethod
	def complete_tags(cls):
		""" build a list of tags and store it in variable b:org_tag_completion
		"""
		heading = Document.current_heading()
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
		for h in Document.headings():
			for t in h.tags:
				all_tags.add(t)

		ignorecase = bool(int(settings.get('org_tags_completion_ignorecase', '0')))
		possible_tags = []
		current_tags = heading.tags
		for t in all_tags:
			if ignorecase:
				if t.lower().startswith(current_tag.lower()):
					possible_tags.append(t)
			elif t.startswith(current_tag):
				possible_tags.append(t)

		vim.command('let b:org_complete_tags = [%s]' % ', '.join(['"%s%s:%s"' % (head, i, tail) for i in possible_tags]))

	@classmethod
	@repeat
	def set_tags(cls):
		""" Set tags for current heading
		"""
		heading = Document.current_heading()
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

	@classmethod
	def realign_tags(cls):
		"""
		Updates tags when user finished editing a heading
		"""
		heading = Document.current_heading()
		if not heading:
			return

		if vim.current.window.cursor[0] == heading.start_vim:
			heading.tags = heading.tags

	@classmethod
	def realign_all_tags(cls):
		"""
		Updates tags when user finishes editing a heading
		"""
		for h in Document.headings():
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

		self.commands.append(Command('OrgTagsRealign', ":py ORGMODE.plugins['TagsProperties'].realign_all_tags()"))

		# workaround to align tags when user is leaving insert mode
		vim.command("""function Org_complete_tags(ArgLead, CmdLine, CursorPos)
python << EOF
ORGMODE.plugins['TagsProperties'].complete_tags()
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
		vim.command("au FileType org :au InsertLeave <buffer> :py ORGMODE.plugins['TagsProperties'].realign_tags()")

		# this is for the current file
		vim.command("au InsertLeave <buffer> :py ORGMODE.plugins['TagsProperties'].realign_tags()")
