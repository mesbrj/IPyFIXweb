"""
General Argument Helper Utilities
"""

def type_check(*expected_types):
    """
    Decorator to check the types of arguments passed to a function or methods at runtime.
    The types needs to be specified in the order of the arguments defined in the function/method signature.
    :param expected_types: Expected types for the arguments.
    :return: Decorated function with type checking.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg, expected in zip(args, expected_types):
                if not isinstance(arg, expected):
                    raise TypeError(f"Expected [{expected}], passed [{type(arg)}]")
            return func(*args, **kwargs)
        return wrapper
    return decorator
