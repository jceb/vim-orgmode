from orgmode import echo, echom, echoe, ORGMODE
from orgmode.menu import Submenu, Separator, ActionEntry
from orgmode.keybinding import Keybinding
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class ShowHide(object):
	""" Example plugin """

	def __init__(self):
		""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = (ORGMODE.orgmenu + Submenu('&Show Hide'), ORGMODE.orgmenu + Separator())

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []
	
	def toggle_folding(self):
		""" Toggle folding similar to the way orgmode does

		This is just a convenience function, don't hesitate to use the z*
		keybindings vim offers to deal with folding!
		"""
		heading = Heading.current_heading()
		if not heading:
			return
		if int(vim.eval('foldclosed(%d)' % heading.start_vim)) != -1:
			# open closed fold
			vim.command('normal %dzo' % heading.number_of_parents)
		else:
			cursor = vim.current.window.cursor[:]
			found_fold = False
			open_depth = 0

			def fold_depth(h):
				if int(vim.eval('foldclosed(%d)' % h.start_vim)) != -1:
					return (h.number_of_parents, True)
				else:
					res = [h.number_of_parents + 1]
					found = False

					for c in h.children:
						d, f = fold_depth(c)
						res.append(d)
						found |= f
						if found:
							break

					return (max(res), found)

			# find deepest fold
			open_depth, found_fold = fold_depth(heading)
			open_depth = open_depth

			def open_fold(h):
				if h.number_of_parents <= open_depth:
					vim.command('normal %dgg%dzo' % (h.start_vim, open_depth))
				if h.children:
					for c in h.children:
						open_fold(c)

			# recursively open folds
			for child in heading.children:
				# find deepest fold
				if found_fold:
					open_fold(child)

			if not found_fold:
				vim.command('%d,%dfoldclose!' % (heading.start_vim, heading.end_of_last_child_vim))

				if heading.number_of_parents:
					# restore cursor position, it might have been changed by open_fold
					vim.current.window.cursor = cursor

					# reopen fold again beacause the former closing of the fold closed all levels, including parents!
					vim.command('normal %dzo' % (heading.number_of_parents, ))

			# restore cursor position
			vim.current.window.cursor = cursor

	def register(self):
		"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		# an Action menu entry which binds "keybinding" to action ":action"
		self.keybindings.append(Keybinding('<Tab>', ':py ORGMODE.plugins["ShowHide"].toggle_folding()<CR>'))
		self.menu[0] + ActionEntry('&Cycle Visibility', self.keybindings[-1])
