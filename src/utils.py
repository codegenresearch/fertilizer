from src.utils import flatten, url_join

def simplify_path_join(*args: str) -> str:
    return url_join(*args)