# -*- coding: utf-8 -*-

import vim
import itertools as it

from orgmode._vim import echom, ORGMODE, apply_count, repeat, realign_tags
from orgmode import settings
from orgmode.liborgmode.base import Direction, flatten_list
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug

# temporary todo states for differnent orgmode buffers
ORGTODOSTATES = {}

from orgmode.py3compat.xrange_compatibility import *
from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *
from orgmode.py3compat.py_py3_string import *


def split_access_key(t, sub=None):
	u""" Split access key

	Args:
		t (str): Todo state
		sub: A value that will be returned instead of access key if there was
			not access key

	Returns:
		tuple: Todo state and access key separated (TODO, ACCESS_KEY)

	Example:
		>>> split_access_key('TODO(t)')
		>>> ('TODO', '(t)')
		>>> split_access_key('WANT', sub='(hi)')
		>>> ('WANT', '(hi)')
	"""
	if type(t) != unicode:
		echom("String must be unicode")
		return (None, None)

	idx = t.find(u'(')

	v, k = (t, sub)
	if idx != -1 and t[idx + 1:-1]:
		v, k = (t[:idx], t[idx + 1:-1])
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
	def _get_next_state(
		cls, current_state, all_states,
		direction=Direction.FORWARD, next_set=False):
		u""" Get the next todo state

		Args:
			current_state (str): The current todo state
			all_states (list): A list containing all todo states within
				sublists. The todo states may contain access keys
			direction: Direction of state or keyword set change (forward or
				backward)
			next_set: Advance to the next keyword set in defined direction.

		Returns:
			str or None: next todo state, or None if there is no next state.

		Note: all_states should have the form of:
			[(['TODO(t)'], ['DONE(d)']),
			 (['REPORT(r)', 'BUG(b)', 'KNOWNCAUSE(k)'], ['FIXED(f)']),
			 ([], ['CANCELED(c)'])]
		"""
		# TODO improve implementation
		if all_states is None:
			return

		# TODO this would not work if there are 2 keys with same name... this
		# also causes problem for find in below method
		def find_current_todo_state(current, all_states, stop=0):
			u""" Find current todo state

			Args:
				current: Current todo state
				all_states: List of todo states
				stop: Internal parameter for parsing only two levels of lists

			Returns:
				list: First position of todo state in list in the form
						(IDX_TOPLEVEL, IDX_SECOND_LEVEL (0|1), IDX_OF_ITEM)
			"""
			for i, element in enumerate(all_states):
				if type(element) in (tuple, list) and stop < 2:
					res = find_current_todo_state(current, element, stop=stop + 1)
					if res:
						res.insert(0, i)
						return res
				# ensure that only on the second level of sublists todo states
				# are found
				if type(element) == unicode and stop == 2:
					if current == split_access_key(element)[0]:
						return [i]

		ci = find_current_todo_state(current_state, all_states)

		# backward direction should really be -1 not 2
		dir = 1
		if direction == Direction.BACKWARD:
			dir = -1
		# work only with top level index
		if next_set:
			top_set = ci[0] if ci is not None else 0
			ind = (top_set + dir) % len(all_states)
			echom("Using set: %s" % str(all_states[ind]))
			# NOTE: List must be flatten because todo states can be empty, this
			# is also valid for above use of flat_list
			return split_access_key(flatten_list(all_states[ind])[0])[0]
		# No next set, cycle around everything
		else:
			tmp = [split_access_key(x)[0] for x in flatten_list(all_states)] + [None]
			# TODO same problem as above if there are 2 todo states with same
			# name
			try:
				ind = (tmp.index(current_state) + dir) % len(tmp)
			except ValueError:
				# TODO should this return None like or first todo item?
				ind = 0
			return tmp[ind]

###############################################################################
# Old code: left until all details are fixed about new code
###############################################################################

		# if ci is None:
		# 	if next_set and direction == Direction.BACKWARD:
		# 		echom(u'Already at the first keyword set')
		# 		return current_state

		# 	if direction == Direction.FORWARD:
		# 		if all_states[0][0]:
		# 			return split_access_key(all_states[0][0][0])[0]
		# 		else:
		# 			return split_access_key(all_states[0][1][0])[0]
		# 	else:
		# 		if all_states[0][1]:
		# 			return split_access_key(all_states[0][1][-1])[0]
		# 		else:
		# 			return split_access_key(all_states[0][0][-1])[0]

		# elif next_set:
		# 	if direction == Direction.FORWARD and ci[0] + 1 < len(all_states[ci[0]]):
		# 		echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] + 1][0]), u', '.join(all_states[ci[0] + 1][1])))
		# 		if all_states[ci[0] + 1][0]:
		# 			return split_access_key(all_states[ci[0] + 1][0][0])[0]
		# 		else:
		# 			return split_access_key(all_states[ci[0] + 1][1][0])[0]

		# 	elif current_state is not None and direction == Direction.BACKWARD and ci[0] - 1 >= 0:
		# 		echom(u'Keyword set: %s | %s' % (u', '.join(all_states[ci[0] - 1][0]), u', '.join(all_states[ci[0] - 1][1])))
		# 		return split_access_key(
		# 			all_states[ci[0] - 1][0][0] if all_states[ci[0] - 1][0] else all_states[ci[0] - 1][1][0])[0]
		# 	else:
		# 		echom(u'Already at the %s keyword set' % (u'first' if direction == Direction.BACKWARD else u'last'))
		# 		return current_state
		# else:
		# 	next_pos = ci[2] + 1 if direction == Direction.FORWARD else ci[2] - 1
		# 	if direction == Direction.FORWARD:
		# 		if next_pos < len(all_states[ci[0]][ci[1]]):
		# 			# select next state within done or todo states
		# 			return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

		# 		elif not ci[1] and next_pos - len(all_states[ci[0]][ci[1]]) < len(all_states[ci[0]][ci[1] + 1]):
		# 			# finished todo states, jump to done states
		# 			return split_access_key(all_states[ci[0]][ci[1] + 1][next_pos - len(all_states[ci[0]][ci[1]])])[0]
		# 	else:
		# 		if next_pos >= 0:
		# 			# select previous state within done or todo states
		# 			return split_access_key(all_states[ci[0]][ci[1]][next_pos])[0]

		# 		elif ci[1] and len(all_states[ci[0]][ci[1] - 1]) + next_pos < len(all_states[ci[0]][ci[1] - 1]):
		# 			# finished done states, jump to todo states
		# 			return split_access_key(all_states[ci[0]][ci[1] - 1][len(all_states[ci[0]][ci[1] - 1]) + next_pos])[0]

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
			if prompt_pos not in [u'botright', u'topleft']:
				prompt_pos = u'botright'

			# pass todo states to new window
			ORGTODOSTATES[d.bufnr] = todo_states
			settings.set(
				u'org_current_state_%d' % d.bufnr,
				current_state if current_state is not None else u'', overwrite=True)
			todo_buffer_exists = bool(int(vim.eval(u_encode(
				u'bufexists("org:todo/%d")' % (d.bufnr, )))))
			if todo_buffer_exists:
				# if the buffer already exists, reuse it
				vim.command(u_encode(
					u'%s sbuffer org:todo/%d' % (prompt_pos, d.bufnr, )))
			else:
				# create a new window
				vim.command(u_encode(
					u'keepalt %s %dsplit org:todo/%d' % (prompt_pos, len(todo_states), d.bufnr)))
		else:
			new_state = Todo._get_next_state(
				current_state, todo_states, direction=direction,
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

		vim_commands = [
			u'let g:org_sav_timeoutlen=&timeoutlen',
			u'au orgmode BufEnter <buffer> :if ! exists("g:org_sav_timeoutlen")|let g:org_sav_timeoutlen=&timeoutlen|set timeoutlen=1|endif',
			u'au orgmode BufLeave <buffer> :if exists("g:org_sav_timeoutlen")|let &timeoutlen=g:org_sav_timeoutlen|unlet g:org_sav_timeoutlen|endif',
			u'setlocal nolist tabstop=16 buftype=nofile timeout timeoutlen=1 winfixheight',
			u'setlocal statusline=Org\\ todo\\ (%s)' % vim.eval(u_encode(u'fnameescape(fnamemodify(bufname(%d), ":t"))' % bufnr)),
			u'nnoremap <silent> <buffer> <Esc> :%sbw<CR>' % vim.eval(u_encode(u'bufnr("%")')),
			u'nnoremap <silent> <buffer> <CR> :let g:org_state = fnameescape(expand("<cword>"))<Bar>bw<Bar>exec "%s ORGMODE.plugins[u\'Todo\'].set_todo_state(\'".g:org_state."\')"<Bar>unlet! g:org_state<CR>' % VIM_PY_CALL,
			]
		# because timeoutlen can only be set globally it needs to be stored and
		# restored later
		# make window a scratch window and set the statusline differently
		for cmd in vim_commands:
			vim.command(u_encode(cmd))

		if all_states is None:
			vim.command(u_encode(u'bw'))
			echom(u'No todo states avaiable for buffer %s' % vim.current.buffer.name)

		for idx, state in enumerate(all_states):
			pairs = [split_access_key(x, sub=u' ') for x in it.chain(*state)]
			line = u'\t'.join(u''.join((u'[%s] ' % x[1], x[0])) for x in pairs)
			vim.current.buffer.append(u_encode(line))
			for todo, key in pairs:
				# FIXME if double key is used for access modified this doesn't work
				vim.command(u_encode(u'nnoremap <silent> <buffer> %s :bw<CR><c-w><c-p>%s ORGMODE.plugins[u"Todo"].set_todo_state("%s")<CR>' % (key, VIM_PY_CALL, u_decode(todo))))

		# position the cursor of the current todo item
		vim.command(u_encode(u'normal! G'))
		current_state = settings.unset(u'org_current_state_%d' % bufnr)
		if current_state is not None and current_state != '':
			for i, buf in enumerate(vim.current.buffer):
				idx = buf.find(current_state)
				if idx != -1:
					vim.current.window.cursor = (i + 1, idx)
					break
			else:
				vim.current.window.cursor = (2, 4)

		# finally make buffer non modifiable
		vim.command(u_encode(u'setfiletype orgtodo'))
		vim.command(u_encode(u'setlocal nomodifiable'))

		# remove temporary todo states for the current buffer
		del ORGTODOSTATES[bufnr]

	def register(self):
		u"""
		Registration of plugin. Key bindings and other initialization should be done.
		"""
		self.keybindings.append(Keybinding(u'<localleader>ct', Plug(
			u'OrgTodoToggleNonInteractive',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=False)<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'&TODO/DONE/-', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<localleader>d', Plug(
			u'OrgTodoToggleInteractive',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state(interactive=True)<CR>' % VIM_PY_CALL)))
		self.menu + ActionEntry(u'&TODO/DONE/- (interactiv)', self.keybindings[-1])

		# add submenu
		submenu = self.menu + Submenu(u'Select &keyword')

		self.keybindings.append(Keybinding(u'<S-Right>', Plug(
			u'OrgTodoForward',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state()<CR>' % VIM_PY_CALL)))
		submenu + ActionEntry(u'&Next keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<S-Left>', Plug(
			u'OrgTodoBackward',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2)<CR>' % VIM_PY_CALL)))
		submenu + ActionEntry(u'&Previous keyword', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Right>', Plug(
			u'OrgTodoSetForward',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state(next_set=True)<CR>' % VIM_PY_CALL)))
		submenu + ActionEntry(u'Next keyword &set', self.keybindings[-1])

		self.keybindings.append(Keybinding(u'<C-S-Left>', Plug(
			u'OrgTodoSetBackward',
			u'%s ORGMODE.plugins[u"Todo"].toggle_todo_state(direction=2, next_set=True)<CR>' % VIM_PY_CALL)))
		submenu + ActionEntry(u'Previous &keyword set', self.keybindings[-1])

		settings.set(u'org_todo_keywords', [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONE')])

		settings.set(u'org_todo_prompt_position', u'botright')

		vim.command(u_encode(u'au orgmode BufReadCmd org:todo/* %s ORGMODE.plugins[u"Todo"].init_org_todo()' % VIM_PY_CALL))

# vim: set noexpandtab:
