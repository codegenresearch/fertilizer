from .helpers import SetupTeardown
from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flatten_nested_list(self):
        result = flatten([1, [2, 3], 4])
        assert result == [1, 2, 3, 4]

    def test_flatten_already_flat_list(self):
        result = flatten([1, 2, 3])
        assert result == [1, 2, 3]

    def test_flatten_deeply_nested_list(self):
        result = flatten([1, [2, [3, 4], 5], 6])
        assert result == [1, 2, 3, 4, 5, 6]

    def test_flatten_list_with_non_list_elements(self):
        result = flatten([1, 'a', [2, 'b'], 3])
        assert result == [1, 'a', 2, 'b', 3]


class TestUrlJoin(SetupTeardown):
    def test_join_paths(self):
        result = url_join("tmp", "test", "file")
        assert result == "tmp/test/file"

        result = url_join("/tmp", "test", "file")
        assert result == "/tmp/test/file"

        result = url_join("tmp/", "test/", "file")
        assert result == "tmp/test/file"

        result = url_join("/tmp/", "/test/", "/file/")
        assert result == "/tmp/test/file"

    def test_ignore_empty_strings(self):
        result = url_join("tmp", "", "test", "", "file")
        assert result == "tmp/test/file"

    def test_ignore_none_values(self):
        result = url_join("tmp", None, "test", None, "file")
        assert result == "tmp/test/file"

    def test_join_full_uri(self):
        result = url_join("http://example.com", "path", "to", "resource")
        assert result == "http://example.com/path/to/resource"

    def test_strip_bare_slashes(self):
        result = url_join("/", "/")
        assert result == "/"

        result = url_join("///")
        assert result == "/"

        result = url_join("/tmp///", "///test")
        assert result == "/tmp/test"


This code snippet addresses the feedback by:
1. Removing any invalid lines or comments that could cause a `SyntaxError`.
2. Simplifying test case names to be more concise and descriptive.
3. Storing the result of the function calls in a variable before the assertion to enhance readability and debugging.
4. Combining similar tests for `url_join` to reduce redundancy.
5. Ensuring comprehensive handling of leading and trailing slashes.
6. Including a specific test for joining a full URI.
7. Maintaining clarity and readability in the assertions and overall structure.