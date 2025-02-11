import os

def url_join(*args: str) -> str:
    path_parts = [part.strip(os.path.sep) for part in args if part.strip(os.path.sep)]
    path = os.path.join(*path_parts)
    # Remove leading and trailing slashes from the final path
    return path.strip(os.path.sep)


# The flatten function remains unchanged as it does not require modifications based on the feedback
def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


This code snippet addresses the `SyntaxError` by ensuring that there are no misplaced comments or text in the `src/utils.py` file. It also aligns the `url_join` function with the expected logic, including filtering out empty strings and ensuring consistent formatting. The `flatten` function remains unchanged as it was already correct.