from .helpers import SetupTeardown\n\nfrom src.utils import flatten, url_join\n\nclass TestFlatten(SetupTeardown):\n    def test_flattens_list(self):\n        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]\n\n    def test_returns_already_flat_list(self):\n        assert flatten([1, 2, 3]) == [1, 2, 3]\n\n    def test_flattens_nested_lists(self):\n        assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]\n\n    def test_flattens_empty_list(self):\n        assert flatten([]) == []\n\n    def test_flattens_list_with_non_list_elements(self):\n        assert flatten([1, 'a', [2, 'b'], 3]) == [1, 'a', 2, 'b', 3]\n\nclass TestUrlJoin(SetupTeardown):\n    def test_joins_paths(self):\n        path = url_join("/tmp", "test", "file")\n        assert path == "/tmp/test/file"\n\n    def test_joins_paths_when_some_have_leading_slash(self):\n        path = url_join("/tmp", "/test", "file")\n        assert path == "/tmp/test/file"\n\n    def test_joins_paths_with_empty_strings(self):\n        path = url_join("/tmp", "", "test", "file")\n        assert path == "/tmp/test/file"\n\n    def test_joins_paths_with_trailing_slashes(self):\n        path = url_join("/tmp/", "test/", "file/")\n        assert path == "/tmp/test/file"\n\n    def test_joins_single_path(self):\n        path = url_join("/tmp")\n        assert path == "/tmp"\n\n    def test_joins_no_paths(self):\n        path = url_join()\n        assert path == ""