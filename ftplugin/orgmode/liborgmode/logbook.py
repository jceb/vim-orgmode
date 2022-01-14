
from orgmode.liborgmode.dom_obj import DomObj, DomObjList
from orgmode.liborgmode.orgdate import OrgDateTime, OrgTimeRange

from orgmode.py3compat.encode_compatibility import *
from orgmode.py3compat.unicode_compatibility import *


class ClockLine(DomObj):
	def __init__(self, date, orig_start=None, *args, **kwargs):
		super(ClockLine, self).__init__(*args, **kwargs)
		self._date = date
		# Force ranges to render as []--[] even if both are on the same day
		self._date.verbose = True
		self._orig_start = orig_start

		self._dirty_clockline = False

	def __unicode__(self):
		if isinstance(self.date, OrgDateTime):
			return u' ' * self.level + u'CLOCK: %s' % self.date
		elif isinstance(self.date, OrgTimeRange):
			self._date.verbose = True
			return u' ' * self.level + u'CLOCK: %s => %s' % (self.date, self.date.str_duration())
		else:
			raise TypeError("self.date is %s instead of OrgDateTime/OrgTimeRange, impossible" % self.date)

	def __str__(self):
		return u_encode(self.__unicode__())

	def set_dirty(self):
		self._dirty_clockline = True
		super(ClockLine, self).set_dirty()

	@property
	def is_dirty(self):
		return self._dirty_clockline

	@property
	def finished(self):
		return isinstance(self.date, OrgTimeRange)

	@property
	def date(self):
		return self._date

	@date.setter
	def date(self, new_date):
		self._date = new_date
		self.set_dirty()


class Logbook(DomObjList):
	pass
