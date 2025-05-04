def type_check(*expected_types):
    """
    Decorator to check the types of arguments passed to a function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for arg, expected in zip(args, expected_types):
                if not isinstance(arg, expected):
                    raise TypeError(f"Expected {expected}, got {type(arg)}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
# Usage:
# @type_check(int, int)
# def add(a, b):
#     return a + b
