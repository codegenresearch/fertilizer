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
        path = url_join("/tmp", "/test", "file")
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