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
    def test_joins_paths(self):
        assert url_join("tmp", "test", "file") == "tmp/test/file"
        assert url_join("/tmp", "test", "file") == "/tmp/test/file"
        assert url_join("tmp/", "test/", "file") == "tmp/test/file"
        assert url_join("/tmp/", "/test/", "/file/") == "/tmp/test/file"

    def test_ignores_empty_strings(self):
        assert url_join("tmp", "", "test", "", "file") == "tmp/test/file"

    def test_ignores_none_values(self):
        assert url_join("tmp", None, "test", None, "file") == "tmp/test/file"

    def test_joins_full_uri(self):
        assert url_join("http://example.com", "path", "to", "resource") == "http://example.com/path/to/resource"

    def test_strips_bare_slashes(self):
        assert url_join("/", "/") == "/"
        assert url_join("///") == "/"
        assert url_join("/tmp///", "///test") == "/tmp/test"


This code snippet addresses the feedback by:
1. Removing the invalid line that caused the `SyntaxError`.
2. Simplifying and consolidating test case names for `url_join`.
3. Combining similar test scenarios into fewer, more comprehensive tests.
4. Adding a test for joining a full URI.
5. Adding a test for stripping bare slashes.