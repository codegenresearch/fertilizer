from .helpers import SetupTeardown

from src.utils import flatten, url_join


class TestFlatten(SetupTeardown):
    def test_flatten_nested_list(self):
        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]

    def test_flatten_already_flat_list(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]


class TestUrlJoin(SetupTeardown):
    def test_joins_paths(self):
        path = url_join("/api", "v1", "resource")
        assert path == "/api/v1/resource"

    def test_joins_paths_with_leading_slashes(self):
        path = url_join("/api", "/v1", "resource")
        assert path == "/api/v1/resource"

    def test_joins_paths_with_trailing_slashes(self):
        path = url_join("/api/", "v1/", "resource")
        assert path == "/api/v1/resource"

    def test_joins_single_path(self):
        path = url_join("/api")
        assert path == "/api"

    def test_joins_empty_paths(self):
        path = url_join("", "v1", "resource")
        assert path == "v1/resource"

    def test_joins_no_paths(self):
        path = url_join()
        assert path == ""

    def test_joins_full_uri(self):
        path = url_join("http://example.com", "/api", "v1", "resource")
        assert path == "http://example.com/api/v1/resource"

    def test_strips_bare_slashes(self):
        path = url_join("/", "/api", "/", "v1", "/", "resource", "/")
        assert path == "/api/v1/resource"

    def test_preserves_leading_slash_in_first_path(self):
        path = url_join("/api", "v1", "resource")
        assert path == "/api/v1/resource"

    def test_removes_extra_slashes(self):
        path = url_join("api", "//v1///resource")
        assert path == "api/v1/resource"


This code snippet addresses the feedback by:
1. Removing any invalid comments or text to ensure syntactic correctness.
2. Revising test method names to be more concise and descriptive.
3. Using API-related paths to match the examples in the gold code.
4. Ensuring that the tests for joining paths account for leading and trailing slashes.
5. Reviewing the expected results in assertions to match the outputs shown in the gold code.
6. Maintaining consistent indentation and spacing.