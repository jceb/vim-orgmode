# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, realign_tags
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command

import vim
import re

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

	uri_match = re.compile(r'^\[{2}(?P<uri>[^][]*)(\]\[(?P<description>[^][]*))?\]{2}')

	@classmethod
	def _get_link(cls, cursor=None):
		u"""
		Get the link the cursor is on and return it's URI and description

		:cursor: None or (Line, Column)
		:returns: None if no link was found, otherwise {uri:URI, description:DESCRIPTION, line:LINE, start:START, end:END} or uri and description could be None if not set
		"""
		cursor = cursor if cursor else vim.current.window.cursor
		line = vim.current.buffer[cursor[0] - 1].decode(u'utf-8')

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

			res = {u'line':line, u'start':start, u'end':end, u'uri':None, u'description':None}
			if match:
				res.update(match.groupdict())
			return res

	@classmethod
	def follow(cls, action=u'openLink', visual=u''):
		u""" Follow hyperlink. If called on a regular string UTL determines the
		outcome. Normally a file with that name will be opened.

		:action: "copy" if the link should be copied to clipboard, otherwise the link will be opened
		:visual: "visual" if Universal Text Linking should be triggered in visual mode

		:returns: URI or None
		"""
		if not int(vim.eval(u'exists(":Utl")')):
			echom(u'Universal Text Linking plugin not installed, unable to proceed.')
			return

		action = u'copyLink' if action and action.startswith(u'copy') else u'openLink'
		visual = u'visual' if visual and visual.startswith(u'visual') else u''

		link = Hyperlinks._get_link()

		if link and link[u'uri'] is not None:
			# call UTL with the URI
			vim.command((u'Utl %s %s %s' % (action, visual, link[u'uri'])).encode(u'utf-8'))
			return link[u'uri']
		else:
			# call UTL and let it decide what to do
			vim.command((u'Utl %s %s' % (action, visual)).encode(u'utf-8'))

	@classmethod
	@realign_tags
	def insert(cls, uri=None, description=None):
		u""" Inserts a hyperlink. If no arguments are provided, an interactive
		query will be started.

		:uri: The URI that will be opened
		:description: An optional description that will be displayed instead of the URI

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
			uri = uri.decode(u'utf-8')

		if description is None:
			description = vim.eval(u'input("Description: ")').decode(u'utf-8')
		elif link:
			description = vim.eval(u'input("Description: ", "%s")' % link[u'description']).decode(u'utf-8')
		if description is None:
			return

		cursor = vim.current.window.cursor
		cl = vim.current.buffer[cursor[0] - 1].decode(u'utf-8')
		head = cl[:cursor[1] + 1] if not link else cl[:link[u'start']]
		tail = cl[cursor[1] + 1:] if not link else cl[link[u'end']:]

		separator = u''
		if description:
			separator = u']['

		if uri or description:
			vim.current.buffer[cursor[0] - 1] = (u''.join((head, u'[[%s%s%s]]' % (uri, separator, description), tail))).encode(u'utf-8')
		elif link:
			vim.current.buffer[cursor[0] - 1] = (u''.join((head, tail))).encode(u'utf-8')

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.commands.append(Command(u'OrgHyperlinkFollow', u':py ORGMODE.plugins[u"Hyperlinks"].follow()'))
		self.keybindings.append(Keybinding(u'gl', Plug(u'OrgHyperlinkFollow', self.commands[-1])))
		self.menu + ActionEntry(u'&Follow Link', self.keybindings[-1])

		self.commands.append(Command(u'OrgHyperlinkCopy', u':py ORGMODE.plugins[u"Hyperlinks"].follow(action=u"copy")'))
		self.keybindings.append(Keybinding(u'gyl', Plug(u'OrgHyperlinkCopy', self.commands[-1])))
		self.menu + ActionEntry(u'&Copy Link', self.keybindings[-1])

		self.commands.append(Command(u'OrgHyperlinkInsert', u':py ORGMODE.plugins[u"Hyperlinks"].insert(<f-args>)', arguments=u'*'))
		self.keybindings.append(Keybinding(u'gil', Plug(u'OrgHyperlinkInsert', self.commands[-1])))
		self.menu + ActionEntry(u'&Insert Link', self.keybindings[-1])

		self.menu + Separator()

		# find next link
		self.commands.append(Command(u'OrgHyperlinkNextLink', u":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 's') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding(u'gn', Plug(u'OrgHyperlinkNextLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Next Link', self.keybindings[-1])

		# find previous link
		self.commands.append(Command(u'OrgHyperlinkPreviousLink', u":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 'bs') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding(u'go', Plug(u'OrgHyperlinkPreviousLink', self.commands[-1])))
		self.menu + ActionEntry(u'&Previous Link', self.keybindings[-1])

		self.menu + Separator()

		# Descriptive Links
		self.commands.append(Command(u'OrgHyperlinkDescriptiveLinks', u':setlocal cole=2'))
		self.menu + ActionEntry(u'&Descriptive Links', self.commands[-1])

		# Literal Links
		self.commands.append(Command(u'OrgHyperlinkLiteralLinks', u':setlocal cole=0'))
		self.menu + ActionEntry(u'&Literal Links', self.commands[-1])
