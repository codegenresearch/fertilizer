import os\nimport pytest\nfrom .helpers import get_torrent_path, SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\nfrom src.parser import (\n    is_valid_infohash,\n    get_source,\n    get_name,\n    get_bencoded_data,\n    get_announce_url,\n    get_origin_tracker,\n    recalculate_hash_for_new_source,\n    save_bencoded_data,\n    calculate_infohash,\n    TorrentDecodingError,\n)\n\n\nclass TestIsValidInfohash(SetupTeardown):\n    def test_returns_true_for_valid_infohash(self):\n        assert is_valid_infohash("0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33")\n\n    def test_returns_false_for_invalid_infohash(self):\n        assert not is_valid_infohash("abc")\n        assert not is_valid_infohash("mnopqrstuvwx")\n        assert not is_valid_infohash("Ubeec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33")\n        assert not is_valid_infohash(123)\n\n\nclass TestGetSource(SetupTeardown):\n    def test_returns_source_if_present(self):\n        assert get_source({b"info": {b"source": b"FOO"}}) == b"FOO"\n\n    def test_returns_none_if_absent(self):\n        assert get_source({}) is None\n\n\nclass TestGetName(SetupTeardown):\n    def test_returns_name_if_present(self):\n        assert get_name({b"info": {b"name": b"foo"}}) == b"foo"\n\n    def test_returns_none_if_absent(self):\n        assert get_name({}) is None\n\n\nclass TestGetAnnounceUrl(SetupTeardown):\n    def test_returns_url_if_present_in_announce(self):\n        assert get_announce_url({b"announce": b"https://foo.bar"}) == [b"https://foo.bar"]\n\n    def test_returns_url_if_present_in_trackers(self):\n        assert get_announce_url({b"trackers": [[b"https://foo.bar"], b"https://baz.qux"]}) == [\n            b"https://foo.bar",\n            b"https://baz.qux",\n        ]\n\n    def test_returns_none_if_absent(self):\n        assert get_announce_url({}) is None\n\n\nclass TestGetOriginTracker(SetupTeardown):\n    def test_returns_red_based_on_source(self):\n        assert get_origin_tracker({b"info": {b"source": b"RED"}}) == RedTracker\n        assert get_origin_tracker({b"info": {b"source": b"PTH"}}) == RedTracker\n\n    def test_returns_ops_based_on_source(self):\n        assert get_origin_tracker({b"info": {b"source": b"OPS"}}) == OpsTracker\n\n    def test_returns_red_based_on_announce(self):\n        assert get_origin_tracker({b"announce": b"https://flacsfor.me/123abc"}) == RedTracker\n\n    def test_returns_ops_based_on_announce(self):\n        assert get_origin_tracker({b"announce": b"https://home.opsfet.ch/123abc"}) == OpsTracker\n\n    def test_returns_red_based_on_trackers(self):\n        assert get_origin_tracker({b"trackers": [[b"https://flacsfor.me/123abc"], b"https://baz.qux"]}) == RedTracker\n\n    def test_returns_ops_based_on_trackers(self):\n        assert get_origin_tracker({b"trackers": [[b"https://home.opsfet.ch/123abc"], b"https://baz.qux"]}) == OpsTracker\n\n    def test_returns_none_if_no_match(self):\n        assert get_origin_tracker({}) is None\n        assert get_origin_tracker({b"info": {b"source": b"FOO"}}) is None\n        assert get_origin_tracker({b"announce": b"https://foo/123abc"}) is None\n\n\nclass TestCalculateInfohash(SetupTeardown):\n    def test_returns_infohash(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        result = calculate_infohash(torrent_data)\n\n        assert result == "FD2F1D966DF7E2E35B0CF56BC8510C6BB4D44467"\n\n    def test_raises_error_if_info_key_missing(self):\n        with pytest.raises(TorrentDecodingError):\n            calculate_infohash({})\n\n\nclass TestRecalculateHashForNewSource(SetupTeardown):\n    def test_replaces_source_and_returns_hash(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        new_source = b"OPS"\n\n        result = recalculate_hash_for_new_source(torrent_data, new_source)\n\n        assert result == "4F36F59992B6F7CB6EB6C2DEE06DD66AC81A981B"\n\n    def test_doesnt_mutate_original_dict(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        new_source = b"OPS"\n\n        recalculate_hash_for_new_source(torrent_data, new_source)\n\n        assert torrent_data == {b"info": {b"source": b"RED"}}\n\n\nclass TestGetTorrentData(SetupTeardown):\n    def test_returns_torrent_data(self):\n        result = get_bencoded_data(get_torrent_path("no_source"))\n\n        assert isinstance(result, dict)\n        assert b"info" in result\n\n    def test_returns_none_on_error(self):\n        result = get_bencoded_data(get_torrent_path("broken"))\n\n        assert result is None\n\n\nclass TestSaveTorrentData(SetupTeardown):\n    def test_saves_torrent_data(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        filename = "/tmp/test_save_bencoded_data.torrent"\n\n        save_bencoded_data(filename, torrent_data)\n\n        with open(filename, "rb") as f:\n            result = f.read()\n\n        assert result == b"d4:infod6:source3:REDee"\n\n        os.remove(filename)\n\n    def test_returns_filename(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        filename = "/tmp/test_save_bencoded_data.torrent"\n\n        result = save_bencoded_data(filename, torrent_data)\n\n        assert result == filename\n\n        os.remove(filename)\n\n    def test_creates_parent_directory(self):\n        torrent_data = {b"info": {b"source": b"RED"}}\n        filename = "/tmp/output/foo/test_save_bencoded_data.torrent"\n\n        save_bencoded_data(filename, torrent_data)\n\n        assert os.path.exists("/tmp/output/foo")\n\n        os.remove(filename)\n