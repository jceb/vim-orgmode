class Todo(object):
	""" Implement todo items """

	def __init__(self):
		object.__init__(self)
		self.menu = ORGMODE.orgmenu + Submenu('&TODO')
		self.keybindings = []

	def register(self):
	    pass

	def unregister(self):
	    pass
