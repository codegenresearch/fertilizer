import os

def flatten(arg):
  if not isinstance(arg, list):
    return [arg]
  return [x for sub in arg for x in flatten(sub)]

def url_join(*args):
  path = []
  for part in args:
    part = part.lstrip(os.path.sep)
    if part and path and path[-1] != os.path.sep:
      path.append(os.path.sep)
    path.append(part)
  return ''.join(path)

class TestFlatten:
  def test_flattens_list(self):
    assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

  def test_returns_already_flat_list(self):
    assert flatten([1, 2, 3]) == [1, 2, 3]

class TestUrlJoin:
  def test_joins_paths(self):
    path = url_join("/api", "v1", "foo")
    assert path == "api/v1/foo"

  def test_joins_paths_when_some_have_leading_trailing_slash(self):
    path = url_join("/api/", "/v1/", "foo/")
    assert path == "api/v1/foo"

  def test_joins_a_full_uri(self):
    path = url_join("https://api.example.com/", "/v1", "foo")
    assert path == "https://api.example.com/v1/foo"

  def test_strips_bare_slashes(self):
    path = url_join("https://api.example.com/", "/", "/v1/", "/foo/", "/")
    assert path == "https://api.example.com/v1/foo"