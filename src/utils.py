from src.utils import url_join

def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


It seems there was a misunderstanding in the initial request. The `flatten` function does not require `url_join` for its functionality. However, to address the test case feedback, I ensured that `url_join` is correctly imported from `src.utils`. If `url_join` is not defined in `src.utils`, it needs to be implemented there. Here is the implementation of `url_join` based on the tests provided:


# src/utils.py
import os

def url_join(*args: str) -> str:
    path_parts = [part.strip(os.path.sep) for part in args]
    path = os.path.join(*path_parts)
    # Remove leading and trailing slashes from the final path
    return path.strip(os.path.sep)


This implementation of `url_join` should align with the test cases provided in `tests/test_utils.py`.