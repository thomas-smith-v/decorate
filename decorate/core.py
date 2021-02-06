from typing import Any, Callable, Dict, Iterable, Tuple, Union
from functools import wraps
import inspect


class precall(object):
    """General function decorator for calling function(s) ~before~ the wrapped functions.
    """
    def __init__(
        self,
        prefunctions: Union[Callable, Iterable[Callable]] = None,
        pass_inputs: bool = False,
        pass_func: bool = False
    ) -> None:
        """General function decorator for calling function(s) ~before~ the wrapped functions.

        Includes optional arguments to pass (1) the original decorated function, and/or (2) the
        args and kwargs that were passed to the original decorated function, to each of the 
        'pre-functions'.

        Note: If the original decorated function is passed, it can always be accessed in the first 
        index of the `args` tuple, i.e., function = `args[0]`

        Args:
            prefunctions (Union[Callable, Iterable[Callable]], optional): Function or list of functions to call before the main function. Defaults to None.
            pass_inputs (bool, optional): Pass the original arguments and keyword arguments to each of the 'pre-functions'. Defaults to False.
            pass_func (bool, optional): Pass the original function to each of the 'pre-functions'. If True, function will be passed in the first index of `args`, i.e. `function = args[0]`. Defaults to False.

        Raises:
            ValueError: If `prefunctions` is not a callable or list of callables.
        """
        if prefunctions is None:
            prefunctions = []

        elif isinstance(prefunctions, Callable):
            prefunctions = [prefunctions]

        elif not isinstance(prefunctions, Iterable):
            raise ValueError(
                f"Argument must be a callable, list of callables, or NoneType. Received '{type(prefunctions)}'")

        self.prefunctions = prefunctions
        self.pass_inputs = pass_inputs
        self.pass_func = pass_func

    def __call__(self, func) -> Any:

        @wraps(func)
        def wrapper(*args, **kwargs):
            cfg = []
            if self.pass_inputs: 
                cfg.append( ArgParser.CONFIG_INCLUDE_ARGS )
                cfg.append( ArgParser.CONFIG_INCLUDE_KWARGS )
                cfg.append( ArgParser.CONFIG_INCLUDE_DEFAULTS )
            
            if self.pass_func:
                cfg.append( ArgParser.CONFIG_INSERT_FUNCTION_AT_FRONT )

            wrapper_args, wrapper_kwargs = ArgParser(func, args, kwargs, cfg).get()

            for fn in self.prefunctions:
                fn(*wrapper_args, **wrapper_kwargs)

            return func(*args, **kwargs)

        return wrapper


class postcall(object):
    """General function decorator for calling function(s) ~before~ the wrapped functions.
    """
    def __init__(
        self,
        postfunctions: Union[Callable, Iterable[Callable]] = None,
        pass_inputs: bool = False,
        pass_func: bool = False,
        pass_output: bool = False
    ) -> None:
        """
        General function decorator for calling function(s) ~before~ the wrapped functions.

        Includes optional arguments to pass (1) the original decorated function, and/or (2) the
        args and kwargs that were passed to the original decorated function, to each of the 
        'pre-functions'.

        Note: If the original decorated function is passed, it can always be accessed in the first 
        index of the `args` tuple, i.e., function = `args[0]`

        Args:
            postfunctions (Union[Callable, Iterable[Callable]], optional): Function or list of functions to call after the main function. Defaults to None.
            pass_inputs (bool, optional): Pass the original arguments and keyword arguments to each of the 'post-functions'. Defaults to False.
            pass_func (bool, optional): Pass the original function to each of the 'post-functions'. If True, function will be passed in the first index of `args`, i.e. `function = args[0]`. Defaults to False.
            pass_output (bool, optional): Pass the original function's output to each of the 'post-functions'. If True, output will be passed in the last index of `args`, i.e. `output = args[-1]`. Defaults to False.

        Raises:
            ValueError: If `postfunctions` is not a callable or list of callables.
        """

        if postfunctions is None:
            postfunctions = []

        elif isinstance(postfunctions, Callable):
            postfunctions = [postfunctions]

        elif not isinstance(postfunctions, Iterable):
            raise ValueError(
                f"Argument must be a callable, list of callables, or NoneType. Received '{type(postfunctions)}'")

        self.postfunctions = postfunctions
        self.pass_inputs = pass_inputs
        self.pass_func = pass_func
        self.pass_output = pass_output

    def __call__(self, func) -> Any:

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            cfg = []

            if self.pass_inputs:
                cfg.append( ArgParser.CONFIG_INCLUDE_ARGS )
                cfg.append( ArgParser.CONFIG_INCLUDE_KWARGS )
                cfg.append( ArgParser.CONFIG_INCLUDE_DEFAULTS )

            if self.pass_func:
                cfg.append( ArgParser.CONFIG_INSERT_FUNCTION_AT_FRONT )

            if self.pass_output:
                cfg.append( (ArgParser.CONFIG_INSERT_OUTPUT_AT_END, result) )

            wrapper_args, wrapper_kwargs = ArgParser(func, args, kwargs, cfg).get()

            for fn in self.postfunctions:
                fn(*wrapper_args, **wrapper_kwargs)

            return result

        return wrapper


class ArgParser(object):
    """Simple argument parser that accepts different configurations.
    """
    CONFIG_INCLUDE_ARGS = 0
    CONFIG_INCLUDE_KWARGS = 1
    CONFIG_INCLUDE_DEFAULTS = 2
    CONFIG_INSERT_FUNCTION_AT_FRONT = 3
    CONFIG_INSERT_OUTPUT_AT_END = 4

    def __init__(self,
                 function:Callable,
                 function_args:Tuple,
                 function_kwargs:Dict,
                 config_sequence:Iterable[Union[int, Tuple[int, Any]]]
                 ) -> None:
        """Simple argument parser that accepts different configurations.

        Usage:
            Supply a function, arguments, and configuration sequences. Call ArgParser::get to retrieve parsed arguments.

        Examples:
        \t To get all arguments, including default arguments, from a function:
            >>> def test_function(default_value='default', *args, **kwargs):
            ...     return args, kwargs
            >>> 
            >>> args = (1, 2)
            >>> kwargs = {'key': 'value'}
            >>> 
            >>> config_sequence = [
            ...     ArgParser.CONFIG_INCLUDE_ARGS, 
            ...     ArgParser.CONFIG_INCLUDE_KWARGS, 
            ...     ArgParser.CONFIG_INCLUDE_DEFAULTS
            ... ] 
            >>> args, kwargs = ArgParser(test_function, args, kwargs, config_sequence).get()
            >>> 
            >>> print(args)
            (1, 2)
            >>> print(kwargs)
            {'key':'value', 'default_value':'default'}

        \t To get only positional arguments, and append a function's output to the end:
            >>> def test_function(*args, **kwargs):
            ...     return True
            >>> 
            >>> args = (1, 2)
            >>> kwargs = {'key': 'value'}
            >>> 
            >>> config_sequence = [
            ...     ArgParser.CONFIG_INCLUDE_ARGS, 
            ...     ( ArgParser.CONFIG_INSERT_OUTPUT_AT_END, test_function() )
            ... ] 
            >>> args, kwargs = ArgParser(test_function, args, kwargs, config_sequence).get()
            >>> 
            >>> print(args)
            (1, 2, True)
            >>> print(kwargs)
            {}

        Args:
            function (Callable): The function in question.
            function_args (Tuple): Arguments that are being supplied to the function
            function_kwargs (Dict): Keyword arguments that are being supplied to the function. Does not include default arguments that were not overwritten.
            config_sequence (Iterable[Union[int, Tuple[int, Any]]], optional): Configuration or sequence of configurations to apply to the supplied arguments.
        """
        self.function = function
        self.function_args = function_args
        self.function_kwargs = function_kwargs
        self.config_sequence = config_sequence

        self.args = ()
        self.kwargs = {}

        self._dict = {
            self.CONFIG_INCLUDE_ARGS: self.include_args,
            self.CONFIG_INCLUDE_KWARGS: self.include_kwargs,
            self.CONFIG_INCLUDE_DEFAULTS: self.include_defaults,
            self.CONFIG_INSERT_FUNCTION_AT_FRONT: self.insert_function_at_front,
            self.CONFIG_INSERT_OUTPUT_AT_END: self.insert_output_at_end
        }

    def get(self) -> Tuple[Tuple, Dict]:
        for config in self.config_sequence:
            
            if isinstance(config, tuple):
                cfg, arg = config
                self._dict[cfg]( arg )

            else:
                self._dict[config]()

        return self.args, self.kwargs

    def include_args(self):
        self.args = self.args + self.function_args
        return self

    def include_kwargs(self):
        self.kwargs.update( self.function_kwargs )
        return self

    def include_defaults(self):
        signature = inspect.signature(self.function)

        # Get all default arguments
        defaults = {
            key: value.default
            for key, value in signature.parameters.items()
            if value.default is not inspect.Parameter.empty
        }

        # Filter for arguments that have not already been overwritten 
        defaults = {
            k: v
            for k, v in defaults.items()
            if k not in self.kwargs.keys()
        }

        self.kwargs.update( defaults )
        return self

    def insert_function_at_front(self):
        self.args = (self.function,) + self.args
        return self

    def insert_output_at_end(self, output):
        self.args = self.args + (output,)
        return self


