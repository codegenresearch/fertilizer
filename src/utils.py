def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


def url_join(*args):
    parts = [str(arg).strip('/') for arg in args]
    return '/'.join([part for part in parts if part])