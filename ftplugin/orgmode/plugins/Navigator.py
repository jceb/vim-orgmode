from orgmode import echo, ORGMODE
from orgmode.menu import SubMenu, HorizontalLine, ActionEntry
from orgmode.heading import Heading, DIRECTION_FORWARD, DIRECTION_BACKWARD

import vim

class Navigator(object):
	""" Implement navigation in org-mode documents """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + SubMenu('Navigate Headings')

	def parent(self):
		"""
		Focus parent heading
		"""
		heading = Heading.current_heading()
		if not heading:
			echo('No heading found')
			return

		if heading.parent:
			vim.current.window.cursor = (heading.parent.start + 1, 0)
		else:
			echo('No parent heading found')

	def _focus_heading(self, direction=DIRECTION_FORWARD):
		"""
		Focus next or previous heading in the given direction

		:direction: True for next heading, False for previous heading
		"""
		heading = Heading.current_heading()
		focus_heading = None
		if not heading:
			if direction == DIRECTION_FORWARD:
				focus_heading = Heading.next_heading(ORGMODE.mode)
			if not (heading or focus_heading):
				echo('No heading found')
				return
		if direction == DIRECTION_BACKWARD:
			if vim.current.window.cursor[0] - 1 != heading.start:
				focus_heading = heading

		if not focus_heading:
			if direction == DIRECTION_FORWARD and heading.children:
				focus_heading = heading.children[0]
			elif direction == DIRECTION_FORWARD and heading.next_sibling:
				focus_heading = heading.next_sibling
			elif direction == DIRECTION_BACKWARD and heading.previous_sibling:
				focus_heading = heading.previous_sibling
				while focus_heading.children:
					focus_heading = focus_heading.children[-1]
			else:
				while heading.level > 1:
					if heading.parent:
						if direction == DIRECTION_FORWARD and heading.parent.next_sibling:
							focus_heading = heading.parent.next_sibling
							break
						elif direction == DIRECTION_BACKWARD:
							focus_heading = heading.parent
							break
						else:
							heading = heading.parent
					else:
						break

		if not focus_heading:
			if direction == DIRECTION_FORWARD:
				echo('Already focussing last heading')
			else:
				echo('Already focussing first heading')
			return

		vim.current.window.cursor = (focus_heading.start + 1, focus_heading.level + 2)

	def previous(self):
		"""
		Focus previous heading
		"""
		self._focus_heading(False)

	def next(self):
		"""
		Focus next heading
		"""
		self._focus_heading(True)

	def register(self):
		self.menu + ActionEntry('Up', ':py ORGMODE.plugins["Navigator"].parent()<CR>', '???')
		self.menu + ActionEntry('Next', ':py ORGMODE.plugins["Navigator"].next()<CR>', '}')
		self.menu + ActionEntry('Previous', ':py ORGMODE.plugins["Navigator"].previous()<CR>', '{')
