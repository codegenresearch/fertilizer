from .helpers import SetupTeardown

from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flattens_nested_list(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_returns_already_flat_list(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_flattens_deeply_nested_list(self):
        assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]

    def test_flattens_list_with_non_list_elements(self):
        assert flatten([1, 'a', [2, 'b'], 3]) == [1, 'a', 2, 'b', 3]


class TestUrlJoin(SetupTeardown):
    def test_joins_paths_without_leading_slash(self):
        path = url_join("tmp", "test", "file")
        assert path == "tmp/test/file"

    def test_joins_paths_with_leading_slash(self):
        path = url_join("/tmp", "test", "file")
        assert path == "/tmp/test/file"

    def test_joins_paths_with_trailing_slash(self):
        path = url_join("tmp/", "test/", "file")
        assert path == "tmp/test/file"

    def test_joins_paths_with_empty_strings(self):
        path = url_join("tmp", "", "test", "", "file")
        assert path == "tmp/test/file"

    def test_joins_paths_with_none_values(self):
        path = url_join("tmp", None, "test", None, "file")
        assert path == "tmp/test/file"

    def test_joins_full_uri(self):
        path = url_join("http://example.com", "path", "to", "resource")
        assert path == "http://example.com/path/to/resource"

    def test_joins_with_leading_and_trailing_slashes(self):
        path = url_join("/tmp/", "/test/", "/file/")
        assert path == "/tmp/test/file"


This code snippet addresses the feedback by:
1. Ensuring the `url_join` function handles leading slashes and `None` values correctly.
2. Adding a test case for joining a full URI.
3. Consolidating tests to cover scenarios with leading and trailing slashes more effectively.
4. Using concise and focused test case names for `url_join`.