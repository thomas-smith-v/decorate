import unittest

from decorate.core import precall

# TODO
class test_precall(unittest.TestCase):
    def argAssertion(self, expectedArgs, *args, **kwargs):
        self.assertEqual(args, expectedArgs)
    
    def kwargAssertion(self, expectedKwargs, *args, **kwargs):
        self.assertEqual(kwargs, expectedKwargs)
    
    def test_constructor(self):
        
        @precall
        def wrapped():
            pass
    
    
        