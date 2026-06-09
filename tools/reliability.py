"""
Tool reliability primitives. Retry with exponential backoff, timeout handling.

Design note: keep this layer thin. We wrap tools, not replace them. The
tool itself stays focused on what it does. The wrapper handles when it
goes wrong.
"""

import time
import functools


def with_retry(max_attempts=3, base_delay=1.0, max_delay=10.0):
    """
    Retry a function on exception with exponential backoff.
    
    On final failure, returns a readable error string instead of raising.
    The LLM can read the error and decide what to do.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        time.sleep(delay)
            return f"Tool failed after {max_attempts} attempts: {type(last_error).__name__}: {str(last_error)}"
        return wrapper
    return decorator