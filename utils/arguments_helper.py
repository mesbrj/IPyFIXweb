"""
General Argument Helper Utilities
"""

def type_check(*expected_types):
    """
    Decorator to check the types of arguments passed to a function or methods at runtime.
    :param expected_types: Expected types for the arguments.
    :return: Decorated function with type checking.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg, expected in zip(args, expected_types):
                if not isinstance(arg, expected):
                    raise TypeError(f"Expected {expected}, got {type(arg)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
