# -*- coding: utf-8 -*-

import vim

from orgmode._vim import ORGMODE, repeat
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode import settings

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.py_py3_string import *

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

		leading_portion = u_decode(vim.eval(u'a:ArgLead'))
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
		# TODO current tags never used...
		current_tags = heading.tags
		for t in all_tags:
			if ignorecase:
				if t.lower().startswith(current_tag.lower()):
					possible_tags.append(t)
			elif t.startswith(current_tag):
				possible_tags.append(t)

		vim.command(u_encode(u'let b:org_complete_tags = [%s]' % u', '.join([u'"%s%s:%s"' % (head, i, tail) for i in possible_tags])))

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
		heading.tags = [x for x in u_decode(res).strip().strip(u':').split(u':') if x.strip() != u'']

		d.write()

		return u'OrgSetTags'

	@classmethod
	def find_tags(cls):
		""" Find tags in current file
		"""
		tags = vim.eval(u'input("Find Tags: ", "", "customlist,Org_complete_tags")')
		if tags is None:
			# user pressed <Esc> abort any further processing
			return

		tags = [x for x in u_decode(tags).strip().strip(u':').split(u':') if x.strip() != u'']
		if tags:
			searchstring = u'\\('
			first = True
			for t1 in tags:
				if first:
					first = False
					searchstring += u'%s' % t1
				else:
					searchstring += u'\\|%s' % t1

				for t2 in tags:
					if t1 == t2:
						continue
					searchstring += u'\\(:[a-zA-Z:]*\\)\\?:%s' % t2
			searchstring += u'\\)'

			vim.command(u'/\\zs:%s:\\ze' % searchstring)
		return u'OrgFindTags'

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
		settings.set(u'org_tag_column', vim.eval(u'&textwidth'))
		settings.set(u'org_tag_completion_ignorecase', int(vim.eval(u'&ignorecase')))

		cmd = Command(
			u'OrgSetTags',
			u'%s ORGMODE.plugins[u"TagsProperties"].set_tags()' % VIM_PY_CALL)
		self.commands.append(cmd)
		keybinding = Keybinding(
			u'<localleader>st',
			Plug(u'OrgSetTags', cmd))
		self.keybindings.append(keybinding)
		self.menu + ActionEntry(u'Set &Tags', keybinding)

		cmd = Command(
			u'OrgFindTags',
			u'%s ORGMODE.plugins[u"TagsProperties"].find_tags()' % VIM_PY_CALL)
		self.commands.append(cmd)
		keybinding = Keybinding(
			u'<localleader>ft',
			Plug(u'OrgFindTags', cmd))
		self.keybindings.append(keybinding)
		self.menu + ActionEntry(u'&Find Tags', keybinding)

		cmd = Command(
			u'OrgTagsRealign',
			u"%s ORGMODE.plugins[u'TagsProperties'].realign_all_tags()" % VIM_PY_CALL)
		self.commands.append(cmd)

		# workaround to align tags when user is leaving insert mode
		vim.command(u_encode(u"function Org_complete_tags(ArgLead, CmdLine, CursorPos)\n"
+ sys.executable.split('/')[-1] + u""" << EOF
ORGMODE.plugins[u'TagsProperties'].complete_tags()
EOF
if exists('b:org_complete_tags')
	let tmp = b:org_complete_tags
	unlet b:org_complete_tags
	return tmp
else
	return []
endif
endfunction"""))

		vim.command(u_encode(u"""function Org_realign_tags_on_insert_leave()
if !exists('b:org_complete_tag_on_insertleave_au')
	:au orgmode InsertLeave <buffer> %s ORGMODE.plugins[u'TagsProperties'].realign_tags()
	let b:org_complete_tag_on_insertleave_au = 1
endif
endfunction""" % VIM_PY_CALL))

		# this is for all org files opened after this file
		vim.command(u_encode(u"au orgmode FileType org call Org_realign_tags_on_insert_leave()"))
		# this is for the current file
		vim.command(u_encode(u"call Org_realign_tags_on_insert_leave()"))

# vim: set noexpandtab:
