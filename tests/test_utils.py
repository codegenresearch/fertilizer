from .helpers import SetupTeardown\n\nfrom src.utils import flatten, url_join\n\nclass TestFlatten(SetupTeardown):\n    def test_flatten_nested_list(self):\n        result = flatten([1, [2, 3], 4])\n        assert result == [1, 2, 3, 4]\n\n    def test_flatten_flat_list(self):\n        result = flatten([1, 2, 3])\n        assert result == [1, 2, 3]\n\n    def test_flatten_deeply_nested(self):\n        result = flatten([1, [2, [3, 4]], 5])\n        assert result == [1, 2, 3, 4, 5]\n\n    def test_flatten_empty_list(self):\n        result = flatten([])\n        assert result == []\n\n    def test_flatten_with_non_list_elements(self):\n        result = flatten([1, 'a', [2, 'b'], 3])\n        assert result == [1, 'a', 2, 'b', 3]\n\nclass TestUrlJoin(SetupTeardown):\n    def test_join_paths_no_slashes(self):\n        result = url_join("/tmp", "test", "file")\n        assert result == "/tmp/test/file"\n\n    def test_join_paths_with_leading_slashes(self):\n        result = url_join("/tmp/", "test", "file")\n        assert result == "/tmp/test/file"\n\n    def test_join_paths_with_trailing_slashes(self):\n        result = url_join("/tmp", "test/", "file/")\n        assert result == "/tmp/test/file"\n\n    def test_join_paths_with_leading_and_trailing_slashes(self):\n        result = url_join("/tmp/", "test/", "file/")\n        assert result == "/tmp/test/file"\n\n    def test_join_full_uri(self):\n        result = url_join("http://example.com", "path", "to", "resource")\n        assert result == "http://example.com/path/to/resource"\n\n    def test_join_single_path(self):\n        result = url_join("/tmp")\n        assert result == "/tmp"\n\n    def test_join_no_paths(self):\n        result = url_join()\n        assert result == ""\n\n    def test_join_paths_with_empty_strings(self):\n        result = url_join("/tmp", "", "test", "file")\n        assert result == "/tmp/test/file"\n\n    def test_join_paths_with_bare_slashes(self):\n        result = url_join("/", "test", "/", "file", "/")\n        assert result == "/test/file"\n