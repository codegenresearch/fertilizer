def flatten(arg):
    if not isinstance(arg, list):
        return [arg]
    return [x for sub in arg for x in flatten(sub)]


def url_join(*args: str) -> str:
    path_parts = [part.strip('/') for part in args if part]
    path = '/'.join(path_parts)

    # Ensure the first part has a leading slash if it was present in the original input
    if args and args[0].startswith('/'):
        path = '/' + path

    return path