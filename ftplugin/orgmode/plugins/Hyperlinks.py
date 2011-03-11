# -*- coding: utf-8 -*-

from orgmode import echo, echom, echoe, ORGMODE, apply_count, repeat
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding, Plug, Command
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim
import re

class Hyperlinks(object):
	""" Hyperlinks plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu('Hyperlinks')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

		# commands for this plugin
		self.commands = []

	def follow(self, action='openLink', visual=''):
		""" Follow hyperlink. If called on a regular string UTL determines the
		outcome. Normally a file with that name will be opened.

		:action: "copy" if the link should be copied to clipboard, otherwise the link will be opened
		:visual: "visual" if Universal Text Linking should be triggered in visual mode

		:returns: URI or None
		"""
		if not int(vim.eval('exists(":Utl")')):
			echom('Universal Text Linking plugin not installed, unable to proceed.')
			return

		action = 'copyLink' if action and action.startswith('copy') else 'openLink'
		visual = 'visual' if visual and visual.startswith('visual') else ''

		cursor = vim.current.window.cursor
		line = vim.current.buffer[cursor[0] - 1]

		# if the cursor is on the last bracket, it's not recognized as a hyperlink
		start = line.rfind('[[', 0, cursor[1])
		end = line.find(']]', cursor[1])
		match = None

		# extract link
		if start != -1 and end != -1:
			uri_match = re.compile('^\[{2}(?P<uri>[^][]*)(\]\[(?P<description>[^][]*))?\]{2}')
			match = uri_match.match(line[start:end + 2])

		if match:
			# call UTL with the URI
			uri = match.groupdict()['uri']
			vim.command('Utl %s %s %s' % (action, visual, uri))
			return uri
		else:
			# call UTL and let it decide what to do
			vim.command('Utl %s %s' % (action, visual))

	def insert(self, uri=None, description=None):
		""" Inserts a hyperlink. If no arguments are provided, an interactive
		query will be started.
		
		:uri: The URI that will be opened
		:description: An optional description that will be displayed instead of the URI
	
		:returns: (URI, description)
	    """
		try:
			if uri == None:
					uri = vim.eval('input("Link: ")')

			if description == None:
				description = vim.eval('input("Description: ")')
				if description:
					description = '][%s' % description

			cursor = vim.current.window.cursor
			cl = vim.current.buffer[cursor[0] - 1]
			# append link after the current cursor position
			vim.current.buffer[cursor[0] - 1] = ''.join((cl[:cursor[1] + 1], '[[%s%s]]' % (uri, description), cl[cursor[1] + 1:]))
		except:
			import traceback
			traceback.print_exc()
			return

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.commands.append(Command('OrgHyperlinkFollow', ':py ORGMODE.plugins["Hyperlinks"].follow()'))
		self.keybindings.append(Keybinding('gl', Plug('OrgHyperlinkFollow', self.commands[-1])))
		self.menu + ActionEntry('&Follow Link', self.keybindings[-1])

		self.commands.append(Command('OrgHyperlinkCopy', ':py ORGMODE.plugins["Hyperlinks"].follow(action="copy")'))
		self.keybindings.append(Keybinding('gyl', Plug('OrgHyperlinkCopy', self.commands[-1])))
		self.menu + ActionEntry('&Copy Link', self.keybindings[-1])

		self.commands.append(Command('OrgHyperlinkInsert', ':py ORGMODE.plugins["Hyperlinks"].insert(<args>)', arguments='*'))
		self.keybindings.append(Keybinding('gil', Plug('OrgHyperlinkInsert', self.commands[-1])))
		self.menu + ActionEntry('&Insert Link', self.keybindings[-1])

		self.menu + Separator()

		# find next link
		self.commands.append(Command('OrgHyperlinkNextLink', ":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 's') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding('gn', Plug('OrgHyperlinkNextLink', self.commands[-1])))
		self.menu + ActionEntry('&Next Link', self.keybindings[-1])

		# find previous link
		self.commands.append(Command('OrgHyperlinkPreviousLink', ":if search('\[\{2}\zs[^][]*\(\]\[[^][]*\)\?\ze\]\{2}', 'bs') == 0 | echo 'No further link found.' | endif"))
		self.keybindings.append(Keybinding('go', Plug('OrgHyperlinkPreviousLink', self.commands[-1])))
		self.menu + ActionEntry('&Previous Link', self.keybindings[-1])

		self.menu + Separator()

		# Descriptive Links
		self.commands.append(Command('OrgHyperlinkDescriptiveLinks', ':setlocal cole=2'))
		self.menu + ActionEntry('&Descriptive Links', self.commands[-1])

		# Literal Links
		self.commands.append(Command('OrgHyperlinkLiteralLinks', ':setlocal cole=0'))
		self.menu + ActionEntry('&Literal Links', self.commands[-1])
