try:
	unicode
except NameError:
	basestring = unicode = str
