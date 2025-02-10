def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


def url_join(*args):
    path_parts = [str(part).strip('/') for part in args if part]
    path = '/'.join(path_parts)
    return path