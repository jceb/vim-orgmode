# -*- coding: utf-8 -*-

import re

import vim

from orgmode._vim import echom, ORGMODE, realign_tags
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.py_py3_string import *

class Hyperlinks(object):
	u""" Hyperlinks plugin """

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'Hyperlinks')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	uri_match = re.compile(
		r'^\[{2}(?P<uri>[^][]*)(\]\[(?P<description>[^][]*))?\]{2}')

	@classmethod
	def _get_link(cls, cursor=None):
		u"""
		Get the link the cursor is on and return it's URI and description

		:cursor: None or (Line, Column)
		:returns: None if no link was found, otherwise {uri:URI,
				description:DESCRIPTION, line:LINE, start:START, end:END}
				or uri and description could be None if not set
		"""
		cursor = cursor if cursor else vim.current.window.cursor
		line = u_decode(vim.current.buffer[cursor[0] - 1])

		# if the cursor is on the last bracket, it's not recognized as a hyperlink
		start = line.rfind(u'[[', 0, cursor[1])
		if start == -1:
			start = line.rfind(u'[[', 0, cursor[1] + 2)
		end = line.find(u']]', cursor[1])
		if end == -1:
			end = line.find(u']]', cursor[1] - 1)

		# extract link
		if start != -1 and end != -1:
			end += 2
			match = Hyperlinks.uri_match.match(line[start:end])

			res = {
				u'line': line,
				u'start': start,
				u'end': end,
				u'uri': None,
				u'description': None}
			if match:
				res.update(match.groupdict())
			# reverse character escaping(partly done due to matching)
			res[u'uri'] = res[u'uri'].replace(u'\\\\', u'\\')
			return res

	@classmethod
	def follow(cls, action=u'openLink', visual=u''):
		u""" Follow hyperlink. If called on a regular string UTL determines the
		outcome. Normally a file with that name will be opened.

		:action: "copy" if the link should be copied to clipboard, otherwise
				the link will be opened
		:visual: "visual" if Universal Text Linking should be triggered in
				visual mode

		:returns: URI or None
		"""
		if not int(vim.eval(u'exists(":Utl")')):
			echom(u'Universal Text Linking plugin not installed, unable to proceed.')
			return

		action = u'copyLink' \
			if (action and action.startswith(u'copy')) \
			else u'openLink'
		visual = u'visual' if visual and visual.startswith(u'visual') else u''

		link = Hyperlinks._get_link()

		if link and link[u'uri'] is not None:
			# call UTL with the URI
			vim.command(u_encode(u'Utl %s %s %s' % (action, visual, link[u'uri'])))
			return link[u'uri']
		else:
			# call UTL and let it decide what to do
			vim.command(u_encode(u'Utl %s %s' % (action, visual)))

	@classmethod
	@realign_tags
	def insert(cls, uri=None, description=None):
		u""" Inserts a hyperlink. If no arguments are provided, an interactive
		query will be started.

		:uri: The URI that will be opened
		:description: An optional description that will be displayed instead of
				the URI

		:returns: (URI, description)
		"""
		link = Hyperlinks._get_link()
		if link:
			if uri is None and link[u'uri'] is not None:
				uri = link[u'uri']
			if description is None and link[u'description'] is not None:
				description = link[u'description']

		if uri is None:
			uri = vim.eval(u'input("Link: ", "", "file")')
		elif link:
			uri = vim.eval(u'input("Link: ", "%s", "file")' % link[u'uri'])
		if uri is None:
			return
		else:
			uri = u_decode(uri)

		# character escaping
		uri = uri.replace(u'\\', u'\\\\\\\\')
		uri = uri.replace(u' ', u'\\ ')

		if description is None:
			description = u_decode(vim.eval(u'input("Description: ")'))
		elif link:
			description = vim.eval(
				u'input("Description: ", "%s")' %
				u_decode(link[u'description']))
		if description is None:
			return

		cursor = vim.current.window.cursor
		cl = u_decode(vim.current.buffer[cursor[0] - 1])
		head = cl[:cursor[1] + 1] if not link else cl[:link[u'start']]
		tail = cl[cursor[1] + 1:] if not link else cl[link[u'end']:]

		separator = u''
		if description:
			separator = u']['

		if uri or description:
			vim.current.buffer[cursor[0] - 1] = \
				u_encode(u''.join((head, u'[[%s%s%s]]' % (uri, separator, description), tail)))
		elif link:
			vim.current.buffer[cursor[0] - 1] = \
				u_encode(u''.join((head, tail)))

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		cmd = Command(
			u'OrgHyperlinkFollow',
			u'%s ORGMODE.plugins[u"Hyperlinks"].follow()' % VIM_PY_CALL)
		self.commands.append(cmd)
		self.keybindings.append(
			Keybinding(u'gl', Plug(u'OrgHyperlinkFollow', self.commands[-1])))
		self.menu + ActionEntry(u'&Follow Link', self.keybindings[-1])

		cmd = Command(
			u'OrgHyperlinkCopy',
			u'%s ORGMODE.plugins[u"Hyperlinks"].follow(action=u"copy")' % VIM_PY_CALL)
		self.commands.append(cmd)
		self.keybindings.append(
			Keybinding(u'gyl', Plug(u'OrgHyperlinkCopy', self.commands[-1])))
		self.menu + ActionEntry(u'&Copy Link', self.keybindings[-1])

		cmd = Command(
			u'OrgHyperlinkInsert',
			u'%s ORGMODE.plugins[u"Hyperlinks"].insert(<f-args>)' % VIM_PY_CALL,
			arguments=u'*')
		self.commands.append(cmd)
		self.keybindings.append(
			Keybinding(u'gil', Plug(u'OrgHyperlinkInsert', self.commands[-1])))
		self.menu + ActionEntry(u'&Insert Link', self.keybindings[-1])

		self.menu + Separator()

		# find next link
		cmd = Command(
			u'OrgHyperlinkNextLink',
			u":if search('\\[\\{2}\\zs[^][]*\\(\\]\\[[^][]*\\)\\?\\ze\\]\\{2}', 's') == 0 | echo 'No further link found.' | endif")
		self.commands.append(cmd)
		self.keybindings.append(
			Keybinding(u'gn', Plug(u'OrgHyperlinkNextLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Next Link', self.keybindings[-1])

		# find previous link
		cmd = Command(
			u'OrgHyperlinkPreviousLink',
			u":if search('\\[\\{2}\\zs[^][]*\\(\\]\\[[^][]*\\)\\?\\ze\\]\\{2}', 'bs') == 0 | echo 'No further link found.' | endif")
		self.commands.append(cmd)
		self.keybindings.append(
			Keybinding(u'go', Plug(u'OrgHyperlinkPreviousLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Previous Link', self.keybindings[-1])

		self.menu + Separator()

		# Descriptive Links
		cmd = Command(u'OrgHyperlinkDescriptiveLinks', u':setlocal cole=2')
		self.commands.append(cmd)
		self.menu + ActionEntry(u'&Descriptive Links', self.commands[-1])

		# Literal Links
		cmd = Command(u'OrgHyperlinkLiteralLinks', u':setlocal cole=0')
		self.commands.append(cmd)
		self.menu + ActionEntry(u'&Literal Links', self.commands[-1])

# vim: set noexpandtab:
