import sys

if sys.version_info < (3,):
	VIM_PY_CALL = u':py'
else:
	VIM_PY_CALL = u':py3'

