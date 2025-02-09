from .helpers import SetupTeardown\nfrom src.utils import flatten, url_join\nclass TestFlatten(SetupTeardown):\n    def test_flattens_list(self):\n        assert flatten([1, [2, 3], 4]) == [1, 2, 3, 4]\n    def test_returns_already_flat_list(self):\n        assert flatten([1, 2, 3]) == [1, 2, 3]