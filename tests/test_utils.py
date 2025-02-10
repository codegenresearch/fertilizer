from .helpers import SetupTeardown

from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flatten_nested_list(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_flatten_already_flat_list(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]


class TestUrlJoin(SetupTeardown):
    def test_joins_paths(self):
        path = url_join("/tmp", "test", "file")
        assert path == "/tmp/test/file"

    def test_joins_paths_with_leading_slashes(self):
        path = url_join("/tmp", "/test", "file")
        assert path == "/tmp/test/file"

    def test_joins_paths_with_trailing_slashes(self):
        path = url_join("/tmp/", "test/", "file")
        assert path == "/tmp/test/file"

    def test_joins_single_path(self):
        path = url_join("/tmp")
        assert path == "/tmp"

    def test_joins_empty_paths(self):
        path = url_join("", "test", "file")
        assert path == "test/file"

    def test_joins_no_paths(self):
        path = url_join()
        assert path == ""

    def test_joins_full_uri(self):
        path = url_join("http://example.com", "/path", "to", "resource")
        assert path == "http://example.com/path/to/resource"

    def test_strips_bare_slashes(self):
        path = url_join("/", "/path", "/", "to", "/", "resource", "/")
        assert path == "/path/to/resource"

    def test_preserves_leading_slash_in_first_path(self):
        path = url_join("/path", "to", "resource")
        assert path == "/path/to/resource"

    def test_removes_extra_slashes(self):
        path = url_join("path", "//to///resource")
        assert path == "path/to/resource"


This code snippet addresses the feedback by:
1. Correcting the syntax error by removing any invalid comments or text.
2. Revising test method names to be more concise and descriptive.
3. Using similar path examples and ensuring consistency in leading and trailing slashes.
4. Ensuring that the expected results in assertions match the expected outputs.
5. Maintaining consistent indentation and spacing.