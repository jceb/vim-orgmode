# -*- coding: utf-8 -*-

import vim
import itertools as it

from orgmode._vim import echom, ORGMODE, apply_count, repeat, realign_tags
from orgmode import settings
from orgmode.liborgmode.base import Direction
from orgmode.menu import Submenu, ActionEntry
from orgmode.keybinding import Keybinding, Plug
from orgmode.exceptions import PluginError

# temporary todo states for different orgmode buffers
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
	def _process_all_states(cls, all_states):
		u""" verify if states defined by user is valid.
		Return cleaned_todo and flattened if is. Raise Exception if not.
		Valid checking:
			* no two state share a same name
		"""
		# TODO Write tests. -- Ron89
		cleaned_todos = [[
			split_access_key(todo)[0] for todo in it.chain.from_iterable(x)]
			for x in all_states] + [[None]]

		flattened_todos = list(it.chain.from_iterable(cleaned_todos))
		if len(flattened_todos) != len(set(flattened_todos)):
			raise PluginError(u"Duplicate names detected in TODO keyword list. Please examine `g/b:org_todo_keywords`")
		# TODO This is the case when there are 2 todo states with the same
		# name. It should be handled by making a simple class to hold TODO
		# states, which would avoid mixing 2 todo states with the same name
		# since they would have a different reference (but same content),
		# albeit this can fail because python optimizes short strings (i.e.
		# they hold the same ref) so care should be taken in implementation
		return (cleaned_todos, flattened_todos)

	@classmethod
	def _get_next_state(
		cls, current_state, all_states, direction=Direction.FORWARD,
		next_set=False):
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
		cleaned_todos, flattened_todos = cls._process_all_states(all_states)

		# backward direction should really be -1 not 2
		next_dir = -1 if direction == Direction.BACKWARD else 1
		# work only with top level index
		if next_set:
			top_set = next((
				todo_set[0] for todo_set in enumerate(cleaned_todos)
				if current_state in todo_set[1]), -1)
			ind = (top_set + next_dir) % len(cleaned_todos)
			if ind != len(cleaned_todos) - 1:
				echom("Using set: %s" % str(all_states[ind]))
			else:
				echom("Keyword removed.")
			return cleaned_todos[ind][0]
		# No next set, cycle around everything
		else:
			ind = next((
				todo_iter[0] for todo_iter in enumerate(flattened_todos)
				if todo_iter[1] == current_state), -1)
			return flattened_todos[(ind + next_dir) % len(flattened_todos)]

	@classmethod
	@realign_tags
	@repeat
	@apply_count
	def toggle_todo_state(
		cls, direction=Direction.FORWARD, interactive=False, next_set=False):
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
			echom(u'No todo states available for buffer %s' % vim.current.buffer.name)

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
		self.menu + ActionEntry(u'&TODO/DONE/- (interactive)', self.keybindings[-1])

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
