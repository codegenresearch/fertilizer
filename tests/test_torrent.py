import os\nimport re\nimport pytest\nimport requests_mock\nfrom .helpers import get_torrent_path, SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\nfrom src.parser import get_bencoded_data, calculate_infohash\nfrom src.errors import TorrentAlreadyExistsError, TorrentDecodingError, UnknownTrackerError, TorrentNotFoundError\nfrom src.torrent import generate_new_torrent_from_file\nclass TestGenerateNewTorrentFromFile(SetupTeardown):\n    def test_saves_new_torrent_from_red_to_ops(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("red_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert os.path.isfile(filepath)\n            assert parsed_torrent[b"announce"] == b"https://home.opsfet.ch/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://orpheus.network/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"OPS"\n            os.remove(filepath)\n\n    def test_saves_new_torrent_from_ops_to_red(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n            os.remove(filepath)\n\n    def test_works_with_qbit_fastresume_files(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("qbit_ops")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n            os.remove(filepath)\n\n    def test_returns_expected_tuple(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            new_tracker, filepath, previously_generated = generate_new_torrent_from_file(\n                torrent_path, "/tmp", red_api, ops_api)\n            get_bencoded_data(filepath)\n            assert os.path.isfile(filepath)\n            assert isinstance(new_tracker, (RedTracker, OpsTracker))\n            assert previously_generated is False\n            os.remove(filepath)\n\n    def test_works_with_alternate_sources_for_creation(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(\n                re.compile(r"action=torrent"),\n                [{"json": self.TORRENT_KNOWN_BAD_RESPONSE}, {"json": self.TORRENT_SUCCESS_RESPONSE}],\n            )\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert filepath == "/tmp/RED/foo [PTH].torrent"\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"PTH"\n            os.remove(filepath)\n\n    def test_works_with_blank_source_for_creation(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(\n                re.compile(r"action=torrent"),\n                [\n                    {"json": self.TORRENT_KNOWN_BAD_RESPONSE},\n                    {"json": self.TORRENT_KNOWN_BAD_RESPONSE},\n                    {"json": self.TORRENT_SUCCESS_RESPONSE},\n                ],\n            )\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert filepath == "/tmp/RED/foo.torrent"\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b""\n            os.remove(filepath)\n\n    def test_raises_error_if_cannot_decode_torrent(self, red_api, ops_api):\n        with pytest.raises(TorrentDecodingError) as excinfo:\n            torrent_path = get_torrent_path("broken")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n        assert str(excinfo.value) == "Error decoding torrent file"\n\n    def test_raises_error_if_tracker_not_found(self, red_api, ops_api):\n        with pytest.raises(UnknownTrackerError) as excinfo:\n            torrent_path = get_torrent_path("no_source")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n        assert str(excinfo.value) == "Torrent not from OPS or RED based on source or announce URL"\n\n    def test_raises_error_if_infohash_found_in_input(self, red_api, ops_api):\n        input_hashes = {"2AEE440CDC7429B3E4A7E4D20E3839DBB48D72C2": "/path/to/foo"}\n        with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n            torrent_path = get_torrent_path("red_source")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api, input_hashes)\n        assert str(excinfo.value) == "Torrent already exists in input directory at /path/to/foo"\n\n    def test_pre_checks_all_infohashes_for_collision(self, red_api, ops_api):\n        input_hashes = {"84508469124335BDE03043105C6E54E00C17B04C": "/path/to/foo"}\n        with requests_mock.Mocker() as m:\n            with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api, input_hashes)\n            assert str(excinfo.value) == "Torrent already exists in input directory at /path/to/foo"\n            assert m.call_count == 0\n\n    def test_returns_appropriately_if_infohash_found_in_output(self, red_api, ops_api):\n        output_hashes = {"2AEE440CDC7429B3E4A7E4D20E3839DBB48D72C2": "bar"}\n        torrent_path = get_torrent_path("red_source")\n        _, _, previously_generated = generate_new_torrent_from_file(\n            torrent_path, "/tmp", red_api, ops_api, {}, output_hashes)\n        assert previously_generated\n\n    def test_returns_appropriately_if_torrent_already_exists(self, red_api, ops_api):\n        filepath = "/tmp/OPS/foo [OPS].torrent"\n        os.makedirs(os.path.dirname(filepath), exist_ok=True)\n        with open(filepath, "w") as f:\n            f.write("")\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("red_source")\n            _, _, previously_generated = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n        assert previously_generated\n        os.remove(filepath)\n\n    def test_raises_error_if_api_response_error(self, red_api, ops_api):\n        with pytest.raises(TorrentNotFoundError) as excinfo:\n            with requests_mock.Mocker() as m:\n                m.get(re.compile(r"action=torrent"), json=self.TORRENT_KNOWN_BAD_RESPONSE)\n                m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n        assert str(excinfo.value) == "Torrent could not be found on OPS"\n\n    def test_raises_error_if_api_response_unknown(self, red_api, ops_api):\n        with pytest.raises(Exception) as excinfo:\n            with requests_mock.Mocker() as m:\n                m.get(re.compile(r"action=torrent"), json=self.TORRENT_UNKNOWN_BAD_RESPONSE)\n                m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n        assert str(excinfo.value) == "An unknown error occurred in the API response from OPS"