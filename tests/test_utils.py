from .helpers import SetupTeardown
from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flatten_nested(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_flatten_already_flat(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_flatten_deeply_nested(self):
        assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]

    def test_flatten_with_non_list_elements(self):
        assert flatten([1, 'a', [2, 'b'], 3]) == [1, 'a', 2, 'b', 3]


class TestUrlJoin(SetupTeardown):
    def test_join_paths(self):
        assert url_join("tmp", "test", "file") == "tmp/test/file"
        assert url_join("/tmp", "test", "file") == "/tmp/test/file"
        assert url_join("tmp/", "test/", "file") == "tmp/test/file"
        assert url_join("/tmp/", "/test/", "/file/") == "/tmp/test/file"

    def test_ignore_empty_strings(self):
        assert url_join("tmp", "", "test", "", "file") == "tmp/test/file"

    def test_ignore_none_values(self):
        assert url_join("tmp", None, "test", None, "file") == "tmp/test/file"

    def test_join_full_uri(self):
        assert url_join("http://example.com", "path", "to", "resource") == "http://example.com/path/to/resource"

    def test_strip_bare_slashes(self):
        assert url_join("/", "/") == "/"
        assert url_join("///") == "/"
        assert url_join("/tmp///", "///test") == "/tmp/test"


This code snippet addresses the feedback by:
1. Removing the invalid line that caused the `SyntaxError`.
2. Simplifying test case names to be more concise and descriptive.
3. Directly asserting the result of the function call without storing it in a variable when it's not necessary.
4. Combining similar tests for `url_join` to reduce redundancy.
5. Ensuring comprehensive handling of leading and trailing slashes.
6. Including a specific test for joining a full URI.
7. Maintaining clarity and readability in the assertions and overall structure.