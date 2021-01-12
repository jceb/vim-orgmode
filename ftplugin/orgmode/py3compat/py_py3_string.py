import sys
from string import Formatter


if sys.version_info < (3,):
    VIM_PY_CALL = u':py'
else:
    VIM_PY_CALL = u':py3'


class NoneAsEmptyFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        v = super().get_value(key, args, kwargs)
        return '' if v is None else v


fmt = NoneAsEmptyFormatter()
