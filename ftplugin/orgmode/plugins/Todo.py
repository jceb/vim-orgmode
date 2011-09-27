# -*- coding: utf-8 -*-

from orgmode import echom, ORGMODE, apply_count, repeat, realign_tags, settings
from orgmode.liborgmode.base import Direction
from orgmode.menu import Submenu, ActionEntry
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
			direction=Direction.FORWARD, interactive=False, next_set=False):
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
			if next_set and direction == Direction.BACKWARD:
				echom(u'Already at the first keyword set')
				return current_state

			return split_access_key(all_states[0][0][0] if all_states[0][0] else all_states[0][1][0])[0] \
					if direction == Direction.FORWARD else \
					split_access_key(all_states[0][1][-1] if all_states[0][1] else all_states[0][0][-1])[0]
		elif next_set:
			if direction == Direction.FORWARD and ci[0] + 1 < len(all_states[ci[0]]):
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] + 1][0]), u', '.join(all_states[ci[0] + 1][1])))
				return split_access_key(all_states[ci[0] + 1][0][0] \
						if all_states[ci[0] + 1][0] else all_states[ci[0] + 1][1][0])[0]
			elif current_state is not None and direction == Direction.BACKWARD and ci[0] - 1 >= 0:
				echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] - 1][0]), u', '.join(all_states[ci[0] - 1][1])))
				return split_access_key(all_states[ci[0] - 1][0][0] \
						if all_states[ci[0] - 1][0] else all_states[ci[0] - 1][1][0])[0]
			else:
				echom(u'Already at the %s keyword set' % (u'first' if direction == Direction.BACKWARD else u'last'))
				return current_state
		else:
			next_pos = ci[2] + 1 if direction == Direction.FORWARD else ci[2] - 1
			if direction == Direction.FORWARD:
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
	def toggle_todo_state(cls, direction=Direction.FORWARD, interactive=False, next_set=False):
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

		# get new state interactively
		if interactive:
			# determine position of the interactive prompt
			prompt_pos = settings.get(u'org_todo_prompt_position', u'botright')
			if not prompt_pos in [u'botright', u'topleft']:
				prompt_pos = u'botright'

			# pass todo states to new window
			ORGTODOSTATES[d.bufnr] = todo_states
			settings.set(u'org_current_state_%d' % d.bufnr, \
					current_state if current_state is not None else u'', overwrite=True)
			todo_buffer_exists = bool(int(vim.eval((u'bufexists("org:todo/%d")'
					% (d.bufnr, )).encode(u'utf-8'))))
			if todo_buffer_exists:
				# if the buffer already exists, reuse it
				vim.command((u'%s sbuffer org:todo/%d' %
						(prompt_pos, d.bufnr, )).encode(u'utf-8'))
			else:
				# create a new window
				vim.command((u'keepalt %s %dsplit org:todo/%d' %
						(prompt_pos, len(todo_states), d.bufnr)).encode(u'utf-8'))
		else:
			new_state = Todo._get_next_state(current_state, todo_states,
					direction=direction, interactive=interactive,
					next_set=next_set)
			cls.set_todo_state(new_state)

		# plug
		plug = u'OrgTodoForward'
		if direction == Direction.BACKWARD:
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

		# set new headline
		heading.todo = state
		d.write_heading(heading)

		# move cursor along with the inserted state only when current position
		# is in the heading; otherwite do nothing
		if heading.start_vim == lineno and colno > heading.level:
			if current_state is not None and \
					colno <= heading.level + len(current_state):
				# the cursor is actually on the todo keyword
				# move it back to the beginning of the keyword in that case
				vim.current.window.cursor = (lineno, heading.level + 1)
			else:
				# the cursor is somewhere in the text, move it along
				if current_state is None and state is None:
					offset = 0
				elif current_state is None and state is not None:
					offset = len(state) + 1
				elif current_state is not None and state is None:
					offset = -len(current_state) - 1
				else:
					offset = len(state) - len(current_state)
				vim.current.window.cursor = (lineno, colno + offset)

	@classmethod
	def init_org_todo(cls):
		u""" Initialize org todo selection window.
		"""
		bufnr = int(vim.current.buffer.name.split('/')[-1])
		all_states = ORGTODOSTATES.get(bufnr, None)

		# because timeoutlen can only be set globally it needs to be stored and restored later
		vim.command(u'let g:org_sav_timeoutlen=&timeoutlen'.encode(u'utf-8'))
		vim.command(u'au orgmode BufEnter <buffer> :if ! exists("g:org_sav_timeoutlen")|let g:org_sav_timeoutlen=&timeoutlen|set timeoutlen=1|endif'.encode(u'utf-8'))
		vim.command(u'au orgmode BufLeave <buffer> :if exists("g:org_sav_timeoutlen")|let &timeoutlen=g:org_sav_timeoutlen|unlet g:org_sav_timeoutlen|endif'.encode(u'utf-8'))
		# make window a scratch window and set the statusline differently
		vim.command(u'setlocal tabstop=16 buftype=nofile timeout timeoutlen=1 winfixheight'.encode(u'utf-8'))
		vim.command((u'setlocal statusline=Org\\ todo\\ (%s)' % vim.eval((u'fnameescape(fnamemodify(bufname(%d), ":t"))' % bufnr).encode(u'utf-8'))).encode(u'utf-8'))
		vim.command((u'nnoremap <silent> <buffer> <Esc> :%sbw<CR>' % (vim.eval(u'bufnr("%")'.encode(u'utf-8')), )).encode(u'utf-8'))
		vim.command(u'nnoremap <silent> <buffer> <CR> :let g:org_state = fnameescape(expand("<cword>"))<Bar>bw<Bar>exec "py ORGMODE.plugins[u\'Todo\'].set_todo_state(\'".g:org_state."\')"<Bar>unlet! g:org_state<CR>'.encode(u'utf-8'))

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
					# WORKAROUND: the cursor can not be positioned properly on
					# the first line. Another line is just inserted and it
					# works great
					vim.current.buffer[0] = u''.encode(u'utf-8')
				vim.current.buffer.append(res.encode(u'utf-8'))

		# position the cursor of the current todo item
		vim.command(u'normal! G'.encode(u'utf-8'))
		current_state = settings.unset(u'org_current_state_%d' % bufnr)
		found = False
		if current_state is not None and current_state != '':
			for i in xrange(0, len(vim.current.buffer)):
				idx = vim.current.buffer[i].find(current_state)
				if idx != -1:
					vim.current.window.cursor = (i + 1, idx)
					found = True
					break
		if not found:
			vim.current.window.cursor = (2, 4)

		# finally make buffer non modifiable
		vim.command(u'setfiletype orgtodo'.encode(u'utf-8'))
		vim.command(u'setlocal nomodifiable'.encode(u'utf-8'))

		# remove temporary todo states for the current buffer
		del ORGTODOSTATES[bufnr]

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding(u'<localleader>ct', Plug(
			u'OrgTodoToggle',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=False)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/-', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>d', Plug(
			u'OrgTodoToggleInteractive',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=True)<CR>')))
		self.menu + ActionEntry(u'&TODO/DONE/- (interactiv)', self.keybindings[-1])

		# add submenu
		submenu = self.menu + Submenu(u'Select &keyword')

		self.keybindings.append(Keybinding(u'<S-Right>', Plug(
			u'OrgTodoForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state()<CR>')))
		submenu + ActionEntry(u'&Next keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Left>', Plug(
			u'OrgTodoBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2)<CR>')))
		submenu + ActionEntry(u'&Previous keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Right>', Plug(
			u'OrgTodoSetForward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(next_set=True)<CR>')))
		submenu + ActionEntry(u'Next keyword &set', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Left>', Plug(
			u'OrgTodoSetBackward',
			u':py ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2, next_set=True)<CR>')))
		submenu + ActionEntry(u'Previous &keyword set', self.keybindings[-1])

		settings.set(u'org_todo_keywords', [u'TODO'.encode(u'utf-8'), u'|'.encode(u'utf-8'), u'DONE'.encode(u'utf-8')])

		settings.set(u'org_todo_prompt_position', u'botright')

		vim.command(u'au orgmode BufReadCmd org:todo/* :py ORGMODE.plugins[u"Todo"].init_org_todo()'.encode(u'utf-8'))

# vim: set noexpandtab:
