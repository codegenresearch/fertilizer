from .helpers import SetupTeardown

from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flattens_list(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_returns_already_flat_list(self):
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

    def test_joins_a_full_uri(self):
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


This code snippet includes additional test cases for `url_join` to cover various scenarios, ensuring that the function behaves as expected. The test method names are more descriptive, and the code formatting is consistent with the style of the gold code.