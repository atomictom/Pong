# Utilities
class Struct(object):
	""" Constructor takes a set of keyword arguments which become the properties of the resulting object"""
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
	def __repr__(self):
		args = ['%s=%s' % (k, repr(v)) for (k,v) in vars(self).items()]
		return 'Struct(%s)' % ', '.join(args)
			
def enum(*sequential, **named):
	""" Creates an enum from named arguments, and unnamed, which are zipped with numbers from 0 to len of the unnamed arg list"""
	return type('Enum', (), dict(zip(sequential, range(len(sequential))), **named))	