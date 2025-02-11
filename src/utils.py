def url_join(*args):
    path_parts = [str(arg).strip('/') for arg in args if str(arg).strip()]
    return '/'.join(path_parts)

# The flatten function remains in its original location or can be moved to utils.py if preferred
def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]