# define Python user-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class InvalidNodeException(Error):
   """Raised when node is invalid"""
   pass