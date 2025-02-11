def url_join(*args):
    return "/".join(str(part).strip("/") for part in args if str(part).strip("/"))


def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


This code snippet addresses the `SyntaxError` by removing the misplaced comment and streamlining the `url_join` function to use a single line with a list comprehension. The `flatten` function remains unchanged as it was already correct.