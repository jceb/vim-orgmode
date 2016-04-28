import sys
if sys.version_info < (3,):
	def u_encode(string):
		return string.encode('utf8')
	def u_decode(string):
		return string.decode('utf8')
else:
	def u_encode(string):
		return string
	def u_decode(string):
		return string
