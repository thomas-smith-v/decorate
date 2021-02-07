from typing import Callable
import unittest

from decorate.core import precall

class test_precall(unittest.TestCase):
    def setUp(self) -> None:
        self._args = []
        self._kwargs = []

    def updateArgs(self, *args, **kwargs):
        self._args.append( args )

    def updateKwargs(self, *args, **kwargs):
        self._kwargs.append( kwargs )

    def emptyFunction(self, *args, **kwargs):
        pass

    def test_initialize_with_no_args(self):
        p = precall()
        self.assertEqual(p.prefunctions, [])
        self.assertEqual(p.pass_inputs, False)
        self.assertEqual(p.pass_func, False)

    def test_initialize_one_function_no_inputs(self):
        p_no_list = precall(prefunctions=self.updateArgs)
        self.assertIsInstance(p_no_list.prefunctions, list)
        self.assertEqual(p_no_list.prefunctions[0], self.updateArgs)
        
        func = p_no_list(self.emptyFunction)
        func(1,2,3,4)
        self.assertEqual(self._args, [()])

        self.setUp()

        p_list = precall(prefunctions=[self.updateArgs])
        self.assertIsInstance(p_list.prefunctions, list)
        self.assertEqual(p_list.prefunctions[0], self.updateArgs)

        func = p_list(self.emptyFunction)
        func(1,2,3,4)
        self.assertEqual(self._args, [()])

    def test_initialize_multiple_functions_no_inputs(self):
        functions = [self.updateArgs, self.updateKwargs]
        p = precall(prefunctions=functions)
        self.assertEqual(p.prefunctions, functions)

        func = p(self.emptyFunction)
        func(1,2,3,4, a=1, b=2, c=3)
        self.assertEqual(self._args, [()])
        self.assertEqual(self._kwargs, [{}])

    def test_pass_inputs(self):
        test_args = ('a', 1, {}, [1,2,3], (1,))
        test_kwargs = {'key1':'value1', 'key2': 2, 'key3': {'subkey1': 'subkey2'}}
        
        @precall(prefunctions=[self.updateArgs, self.updateKwargs], pass_inputs=True)
        def test_func(*args, **kwargs):
            pass

        self.assertEqual(0, len(self._args))
        self.assertEqual(0, len(self._kwargs))

        test_func(*test_args, **test_kwargs)

        for arg in self._args:
            self.assertEqual(arg, test_args)

        for kwarg in self._kwargs:
            self.assertEqual(kwarg, test_kwargs)
    
    def test_pass_function(self):
        test_args = ('a', 1, {}, [1,2,3], (1,))
        
        @precall(prefunctions=[self.updateArgs], pass_func=True)
        def test_func(*args, **kwargs):
            pass

        self.assertEqual(0, len(self._args))
        self.assertEqual(0, len(self._kwargs))

        test_func(*test_args)

        for arg in self._args:
            self.assertEqual(1, len(arg))
            self.assertIsInstance(arg[0], Callable)
            self.assertEqual(arg[0].__name__, test_func.__name__)
    
        