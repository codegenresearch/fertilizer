from .helpers import SetupTeardown

from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flattens_list(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_returns_already_flat_list(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]


class TestUrlJoin(SetupTeardown):
    def test_joins_paths_with_leading_slash(self):
        path = url_join("/tmp", "test", "file")
        assert path == "/tmp/test/file"

    def test_joins_paths_with_trailing_slash(self):
        path = url_join("/tmp/", "test/", "file")
        assert path == "/tmp/test/file"

    def test_joins_paths_with_empty_strings(self):
        path = url_join("/tmp", "", "test", "file")
        assert path == "/tmp/test/file"

    def test_joins_single_path_with_leading_slash(self):
        path = url_join("/tmp")
        assert path == "/tmp"

    def test_joins_single_path_without_leading_slash(self):
        path = url_join("tmp")
        assert path == "tmp"

    def test_joins_no_paths(self):
        path = url_join()
        assert path == ""

    def test_joins_full_uri(self):
        path = url_join("http://example.com", "path", "to", "resource")
        assert path == "http://example.com/path/to/resource"

    def test_strips_bare_slashes(self):
        path = url_join("/", "/", "/")
        assert path == "/"

    def test_joins_paths_without_leading_slash(self):
        path = url_join("tmp", "test", "file")
        assert path == "tmp/test/file"


This code snippet includes additional test cases to cover more scenarios and ensures that the expected outputs match the behavior described in the feedback. The test method names are more descriptive, and the code style is consistent with the provided examples.