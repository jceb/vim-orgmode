import sys
if sys.version_info < (3,):
	def u_encode(string):
		return string.encode('utf8')
else:
	def u_encode(string):
		return string
