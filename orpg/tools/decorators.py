import warnings
import functools

from orpg.orpgCore import *

def deprecated(msg=None):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def wrap(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            out = msg
            if not out:
                out = "Call to deprecated function %s."
            else:
                out = "Call to deprecated function %s.\n" + out

            warnings.warn_explicit(
                out % (func.__name__),
                category=DeprecationWarning,
                filename=func.func_code.co_filename,
                lineno=func.func_code.co_firstlineno + 1
            )
            return func(*args, **kwargs)
        return new_func
    return wrap

def pending_deprecation(msg=None):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def wrap(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            out = msg
            if not out:
                out = "%s is Pending Deprecation."
            else:
                out = "%s is Pending Deprecation.\n" + out

            warnings.warn_explicit(
                out % (func.__name__),
                category=PendingDeprecationWarning,
                filename=func.func_code.co_filename,
                lineno=func.func_code.co_firstlineno + 1
            )
            return func(*args, **kwargs)
        return new_func
    return wrap

def synchronized(lock):
    """
    Synchronization decorator.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return new_func

class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        try:
            return self.cache[args + kwargs.values()]
        except KeyError:
            self.cache[args] = value = self.func(*args, **kwargs)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """
        Return the function's docstring.
        """
        return self.func.__doc__

def debugging(func):
    """
    Decorator to print Enter/Exit debugging info
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        from orpg_log import logger

        if not ORPG_DEBUG & logger.log_level:
            return func(*args, **kwargs)

        if str(args[0].__class__).startswith('<class'):
            cls = args[0].__class__.__name__
            args_s = "self"
            if len(args) > 1:
                args_s += ', ' + ', '.join([str(attr) for attr in args[1:]])
            kwargs_s = ""
            for k,v in kwargs.iteritems():
                kwargs_s += ', ' + k + '=' + str(v)

            call_str = '%(cls)s->%(fnc)s(%(args)s%(kwargs)s)' % {
                'cls':cls,
                'fnc':func.__name__,
                'args':args_s,
                'kwargs':kwargs_s}
            try:
                logger.debug("Enter " + call_str)
                return func(*args, **kwargs)
            finally:
                logger.debug("Exit " + call_str)
        else:
            try:
                logger.debug("Enter " + func.__name__)
                return func(*args, **kwargs)
            finally:
                logger.debug("Exit " + func.__name__)
    return new_func

"""
Cannot use this decorator till we stop supporting py2.5
as class decorators did not land till py2.6 I am just adding it here
So when we do we can convert all singleton classes to use it
"""
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
