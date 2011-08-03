# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, apply_count, repeat, realign_tags, DIRECTION_FORWARD, DIRECTION_BACKWARD
from orgmode.menu import Submenu, ActionEntry
from orgmode import settings
from orgmode.keybinding import Keybinding, Plug

import vim

# temporary todo states for differnent orgmode buffers
ORGTODOSTATES = {}

def split_access_key(t):
	u"""
	:t:		todo state

	:return:	todo state and access key separated (TODO, ACCESS_KEY)
	"""
	if type(t) != unicode:
		return (None, None)

	idx = t.find(u'(')
	v, k = ((t[:idx], t[idx + 1:-1]) if t[idx + 1:-1] else (t, None)) if idx != -1 else (t, None)
	return (v, k)

class Todo(object):
	u"""
	Todo plugin.

	Description taken from orgmode.org:

	You can use TODO keywords to indicate different sequential states in the
	process of working on an item, for example:

	["TODO", "FEEDBACK", "VERIFY", "|", "DONE", "DELEGATED"]

	The vertical bar separates the TODO keywords (states that need action) from
	the DONE states (which need no further action). If you don't provide the
	separator bar, the last state is used as the DONE state. With this setup,
	the command ``,d`` will cycle an entry from TODO to FEEDBACK, then to
	VERIFY, and finally to DONE and DELEGATED.
	"""

	def __init__(self):
		u""" Initialize plugin """
		object.__init__(self)
		# menu entries this plugin should create
		self.menu = ORGMODE.orgmenu + Submenu(u'&TODO Lists')

		# key bindings for this plugin
		# key bindings are also registered through the menu so only additional
		# bindings should be put in this variable
		self.keybindings = []

	@classmethod
	def _get_next_state(cls, current_state, all_states,
			direction=DIRECTION_FORWARD, interactive=False, next_set=False):
		u"""
		:current_state:		the current todo state
		:all_states:		a list containing all todo states within sublists.
							The todo states may contain access keys
		:direction:			direction of state or keyword set change (forward/backward)
		:interactive:		if interactive and more than one todo sequence is
							specified, open a selection window
		:next_set:			advance to the next keyword set in defined direction

		:return:			return the next state as string, or NONE if the
							next state is no state.
		"""
		if not all_states:
			return

		def find_current_todo_state(c, a, stop=0):
			u"""
			:c:		current todo state
			:a:		list of todo states
			:stop:	internal parameter for parsing only two levels of lists

			:return:	first position of todo state in list in the form
						(IDX_TOPLEVEL, IDX_SECOND_LEVEL (0|1), IDX_OF_ITEM)
			"""
			for i in xrange(0, len(a)):
				if type(a[i]) in (tuple, list) and stop < 2:
					r = find_current_todo_state(c, a[i], stop=stop + 1)
					if r:
						r.insert(0, i)
						return r
				# ensure that only on the second level of sublists todo states
				# are found
				if type(a[i]) == unicode and stop == 2:
					_i = split_access_key(a[i])[0]
					if c == _i:
						return [i]

		ci = find_current_todo_state(current_state, all_states)

		if not ci:
			if next_set and direction == DIRECTION_BACKWARD:
				echom(u'Already at the first keyword set')
				return current_state

			return split_access_key(all_states[0][0][0] if all_states[0][0] else all_states[0][1][0])[0] \
					if direction == DIRECTION_FORWARD else \
					split_access_key(all_states[0][1][-1] if all_states[0][1] else all_states[0][0][-1])[0]
		elif next_set:
			if direction == DIRECTION_FORWARD and ci[0] + 1 < len(all_states[ci[0]]):
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] + 1][0]), u', '.join(all_states[ci[0] + 1][1])))
				return split_access_key(all_states[ci[0] + 1][0][0] \
						if all_states[ci[0] + 1][0] else all_states[ci[0] + 1][1][0])[0]
			elif current_state is not None and direction == DIRECTION_BACKWARD and ci[0] - 1 >= 0:
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] - 1][0]), u', '.join(all_states[ci[0] - 1][1])))
				return split_access_key(all_states[ci[0] - 1][0][0] \
						if all_states[ci[0] - 1][0] else all_states[ci[0] - 1][1][0])[0]
			else:
				echom(u'Already at the %s keyword set' % (u'first' if direction == DIRECTION_BACKWARD else u'last'))
				return current_state
		else:
			next_pos = ci[2] + 1 if direction == DIRECTION_FORWARD else ci[2] - 1
			if direction == DIRECTION_FORWARD:
				if next_pos < len(all_states[ci[0]][ci[1]]):
					# select next state within done or todo states
					return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

				elif not ci[1] and next_pos - len(all_states[ci[0]][ci[1]]) < len(all_states[ci[0]][ci[1] + 1]):
					# finished todo states, jump to done states
					return split_access_key(all_states[ci[0]][ci[1] + 1][next_pos - len(all_states[ci[0]][ci[1]])])[0]
			else:
				if next_pos >= 0:
					# select previous state within done or todo states
					return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

				elif ci[1] and len(all_states[ci[0]][ci[1] - 1]) + next_pos < len(all_states[ci[0]][ci[1] - 1]):
					# finished done states, jump to todo states
					return split_access_key(all_states[ci[0]][ci[1] - 1][len(all_states[ci[0]][ci[1] - 1]) + next_pos])[0]

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def toggle_todo_state(cls, direction=DIRECTION_FORWARD, interactive=False, next_set=False):
		u""" Toggle state of TODO item

		:returns: The changed heading
		"""
		d = ORGMODE.get_document(allow_dirty=True)

		# get heading
		heading = d.find_current_heading()
		if not heading:
			vim.eval(u'feedkeys("^", "n")')
			return

		todo_states = d.get_todo_states(strip_access_key=False)
		# get todo states
		if not todo_states:
			echom(u'No todo keywords configured.')
			return

		current_state = heading.todo

		# get new state
		if interactive:
			# pass todo states to new window
			ORGTODOSTATES[d.bufnr] = todo_states
			# create a new window
			vim.command((u'keepalt %dsp org:todo/%d' % (len(todo_states), d.bufnr)).encode(u'utf-8'))
		else:
			new_state = Todo._get_next_state(current_state, todo_states, \
					direction=direction, interactive=interactive, next_set=next_set)
			cls.set_todo_state(new_state)

		# plug
		plug = u'OrgTodoForward'
		if direction == DIRECTION_BACKWARD:
			plug = u'OrgTodoBackward'

		return plug

	@classmethod
	def set_todo_state(cls, state):
		u""" Set todo state for buffer.

		:bufnr:		Number of buffer the todo state should be updated for
		:state:		The new todo state
		"""
		lineno, colno = vim.current.window.cursor
		d = ORGMODE.get_document(allow_dirty=True)
		heading = d.find_current_heading()

		if not heading:
			return

		current_state = heading.todo

		# move cursor along with the inserted state only when current position
		# is in the heading; otherwite do nothing
		if heading.start_vim == lineno:
			if current_state is None and state is None:
				offset = 0
			elif current_state is None:
				offset = len(state)
			elif state is None:
				offset = -len(current_state)
			else:
				offset = len(current_state) - len(state)
			vim.current.window.cursor = (lineno, colno + offset)

		# set new headline
		heading.todo = state
		d.write_heading(heading)

		vim.command(u'set timeoutlen=1000'.encode(u'utf-8'))
		vim.command(u'doau orgmode BufEnter'.encode(u'utf-8'))

	@classmethod
	def init_org_todo(cls):
		u""" Initialize org todo selection window.
		"""
		# make window a scratch window, leaving the window is not possible!
		vim.command(u'setlocal tabstop=16 buftype=nofile timeout timeoutlen=1'.encode(u'utf-8'))
		vim.command(u'nnoremap <silent> <buffer> <Esc> :bw<CR>'.encode(u'utf-8'))
		vim.command((u'nnoremap <silent> <buffer> <CR> :let g:org_state = fnameescape(expand("<cword>"))<Bar>bw<Bar>exec "py ORGMODE.plugins[u\'Todo\'].set_todo_state(\'".g:org_state."\')"<Bar>unlet! g:org_state<CR>').encode(u'utf-8') )
		vim.command(u'au orgmode BufLeave <buffer> :silent! %sbw' % \
				(vim.eval(u'bufnr("%")'.encode(u'utf-8')).decode(u'utf-8')).encode(u'utf-8'))
		bufnr = int(vim.current.buffer.name.split('/')[-1])
		all_states = ORGTODOSTATES.get(bufnr, None)

		if all_states is None:
			vim.command(u'bw'.encode(u'utf-8'))
			echom(u'No todo states avaiable for buffer %s' % vim.current.buffer.name)

		for l in xrange(0, len(all_states)):
			res = u''
			did_done = False
			for j in xrange(0, 2):
				if j < len(all_states[l]):
					for i in all_states[l][j]:
						if type(i) != unicode:
							continue
						v, k = split_access_key(i)
						if k:
							res += (u'\t' if res else u'') + u'[%s] %s' % (k, v)
							# map access keys to callback that updates current heading
							# map selection keys
							vim.command((u'nnoremap <silent> <buffer> %s :bw<Bar>py ORGMODE.plugins[u"Todo"].set_todo_state("%s".decode(u"utf-8"))<CR>' % (k, v)).encode(u'utf-8') )
						elif v:
							res += (u'\t' if res else u'') + v
			if res:
				if l == 0:
					vim.current.buffer[0] = res.encode(u'utf-8')
				else:
					vim.current.buffer.append(res.encode(u'utf-8'))

		# finally make buffer non modifiable
		vim.command(u'setf orgtodo'.encode(u'utf-8'))
		vim.command(u'setlocal nomodifiable'.encode(u'utf-8'))

		# remove temporary todo states for the current buffer
		del ORGTODOSTATES[bufnr]

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		settings.set(u'org_leader', u',')
		leader = settings.get(u'org_leader', u',')

		self.keybindings.append(Keybinding(u'%sd' % leader, Plug(
			u'OrgTodoToggle',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=True)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/-', self.keybindings[-1])
		submenu = self.menu + Submenu(u'Select &keyword')

		self.keybindings.append(Keybinding(u'<S-Right>', Plug(
			u'OrgTodoForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry(u'&Next keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Left>', Plug(
			u'OrgTodoBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=False)<CR>')))
		submenu + ActionEntry(u'&Previous keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Right>', Plug(
			u'OrgTodoSetForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(next_set=True)<CR>')))
		submenu + ActionEntry(u'Next keyword &set', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Left>', Plug(
			u'OrgTodoSetBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=False, next_set=True)<CR>')))
		submenu + ActionEntry(u'Previous &keyword set', self.keybindings[-1])

		settings.set(u'org_todo_keywords', [u'TODO'.encode(u'utf-8'), u'|'.encode(u'utf-8'), u'DONE'.encode(u'utf-8')])

		vim.command(u'au orgmode BufReadCmd org:todo/* :py ORGMODE.plugins[u"Todo"].init_org_todo()'.encode(u'utf-8'))

# vim: set noexpandtab:
