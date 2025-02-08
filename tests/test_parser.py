import os\nfrom .helpers import get_torrent_path, SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\nfrom src.parser import (\n    is_valid_infohash,\n    get_source,\n    get_name,\n    get_bencoded_data,\n    get_announce_url,\n    get_origin_tracker,\n    recalculate_hash_for_new_source,\n    save_bencoded_data,\n    calculate_infohash,\n)\n\nclass TestIsValidInfohash(SetupTeardown):\n    def test_returns_true_for_valid_infohash(self):\n        assert is_valid_infohash(\