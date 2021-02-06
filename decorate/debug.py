import logging
from functools import wraps
from datetime import datetime

from .core import ArgParser


def debug(func):
    """Decorator to debug a function's inputs and outputs. Uses the built-in 'logging' module.\n
    Inputs are logged via `decorate.debug.debug_input`, and follow the format: \n
        `'Datetime' | ['action'] 'function' | args=(args,) | kwargs={kwargs:values}`
    Logged input example:
        `2021-02-05T17:36:53.276937 | [CALL] 'hello' | args=('World',) | kwargs={'punctuation': '!'}`
    
    Outputs are logged via `decorate.debug.debug_output`, and follow the format: \n
        `'Datetime' | ['action'] 'function' | output='output'`
    Logged output example:
        `2021-02-05T17:36:53.276937 | [RETURN] 'hello' | output="Hello, World!"`


    Args:
        func (Callable): Function to decorate

    Returns:
        Callable: Wrapped function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        debug_input(func, deco=False, input_args=args, input_kwargs=kwargs)
        result = func(*args, **kwargs)
        debug_output(func, deco=False, output=result)
        return result

    return wrapper


def debug_input(func, deco=True, input_args=None, input_kwargs=None):
    """A standalone or decorator function for debugging a function's inputs. 
    
    When `deco` is False, the function can be called with supplied args and kwargs. In this
    case, the function does not return a wrapper, but still perfoms the intended functionality.
    When `deco` is True, it behaves as a normal decorator.

    Using the built-in 'logging' module, inputs are logged via the following format:\n
        `'Datetime' | ['action'] 'function' | args=(args,) | kwargs={kwargs:values}`
    Example:
        `2021-02-05T17:36:53.276937 | [CALL] 'hello' | args=('World',) | kwargs={'punctuation': '!'}`

    Args:
        func (Callable): Function to wrap
        deco (bool, optional): If true, function behaves as a normal decorator. If false, the function can be called seperately without returning a wrapper. Defaults to True.
        input_args (tuple, optional): Optional function args to pass if `deco` is False. Defaults to None.
        input_kwargs (dict, optional): Optional function kwargs to pass if `deco` is False. Defaults to None.

    Returns:
        Union[Callable, None]: Wrapped function if `deco` is True. None if `deco` is False.
    """
    
    logger = logging.getLogger( func.__module__ )

    def messages(*args, **kwargs):
        msgs = []
        msgs.append(f"{datetime.now().isoformat()} | [CALL] '{func.__name__}' | args={args} | kwargs={kwargs}") 
        return msgs
    
    if not deco:
        cfg_seq = [
            ArgParser.CONFIG_INCLUDE_ARGS,
            ArgParser.CONFIG_INCLUDE_KWARGS,
            ArgParser.CONFIG_INCLUDE_DEFAULTS
        ]

        full_args, full_kwargs = ArgParser(func, input_args, input_kwargs, config_sequence=cfg_seq).get()

        msgs = messages(*full_args, **full_kwargs)
        for msg in msgs:
            logger.debug( msg )
        return

    @wraps(func)
    def wrapper(*args, **kwargs):
        cfg_seq = [
            ArgParser.CONFIG_INCLUDE_ARGS,
            ArgParser.CONFIG_INCLUDE_KWARGS,
            ArgParser.CONFIG_INCLUDE_DEFAULTS
        ]

        full_args, full_kwargs = ArgParser(func, args, kwargs, config_sequence=cfg_seq).get()

        msgs = messages(*full_args, **full_kwargs)
        for msg in msgs:
            logger.debug( msg )
        return func(*args, **kwargs)

    return wrapper
    
def debug_output(func, deco=True, output=None):
    """A standalone or decorator function for debugging a function's outputs. 
    
    When `deco` is False, the function can be called with previously obtained output. In this
    case, the function does not return a wrapper, but still perfoms the intended functionality.
    When `deco` is True, it behaves as a normal decorator.

    Using the built-in 'logging' module, outputs are logged via the following format:\n
        `'Datetime' | ['action'] 'function' | output='output'`
    Example:
        `2021-02-05T17:36:53.276937 | [RETURN] 'hello' | output="Hello, World!"`

    Args:
        func (Callable): Function to wrap
        deco (bool, optional): If true, function behaves as a normal decorator. If false, the function can be called seperately without returning a wrapper. Defaults to True.
        input_args (tuple, optional): Optional function args to pass if `deco` is False. Defaults to None.
        input_kwargs (dict, optional): Optional function kwargs to pass if `deco` is False. Defaults to None.

    Returns:
        Union[Callable, None]: Wrapped function if `deco` is True. None if `deco` is False.
    """
    logger = logging.getLogger( func.__module__ )

    def messages(opt):
        msgs = []
        msgs.append(f"{datetime.now().isoformat()} | [RETURN] '{func.__name__}' | output={opt}")
        return msgs
    
    if not deco:
        msgs = messages(output)
        for msg in msgs:
            logger.debug( msg )
        return


    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        msgs = messages( result )
        for msg in msgs:
            logger.debug( msg )
        return result

    return wrapper