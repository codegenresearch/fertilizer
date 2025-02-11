import os

def url_join(*args):
    path_parts = [str(part).strip("/") for part in args if str(part).strip("/")]
    return "/".join(path_parts)


def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


This code snippet addresses the `SyntaxError` by removing type hints from the `url_join` function and using string manipulation to join the parts with a "/" separator. It also ensures that each argument is converted to a string before stripping. The `flatten` function remains unchanged as it was already correct.