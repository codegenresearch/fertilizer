import os\nimport re\nimport pytest\nimport requests_mock\nfrom .helpers import get_torrent_path, SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\nfrom src.parser import get_bencoded_data, calculate_infohash\nfrom src.errors import TorrentAlreadyExistsError, TorrentDecodingError, UnknownTrackerError, TorrentNotFoundError\nfrom src.torrent import generate_new_torrent_from_file\nclass TestGenerateNewTorrentFromFile(SetupTeardown):\n    def test_saves_new_torrent_from_red_to_ops(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile("action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile("action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("red_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert os.path.isfile(filepath)\n            assert parsed_torrent[b"announce"] == b"https://home.opsfet.ch/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://orpheus.network/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"OPS"\n            os.remove(filepath)\n    def test_saves_new_torrent_from_ops_to_red(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile("action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile("action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n            os.remove(filepath)\n    def test_works_with_qbit_fastresume_files(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile("action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile("action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("qbit_ops")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n            os.remove(filepath)\n    def test_returns_expected_tuple(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile("action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile("action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            new_tracker, filepath, previously_generated = generate_new_torrent_from_file(\n                torrent_path, "/tmp", red_api, ops_api)\n            get_bencoded_data(filepath)\n            assert os.path.isfile(filepath)\n            assert new_tracker == RedTracker or new_tracker == OpsTracker  # Adjust based on expected tracker\n            assert previously_generated is False\n            os.remove(filepath)\n    def test_works_with_alternate_sources_for_creation(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(\n                re.compile("action=torrent"),\n                [{"json": self.TORRENT_KNOWN_BAD_RESPONSE}, {"json": self.TORRENT_SUCCESS_RESPONSE}],\n            )\n            m.get(re.compile("action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath, _ = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n            assert filepath == "/tmp/RED/foo [PTH].torrent"\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"PTH"\n            os.remove(filepath)\n    def test_works_with_blank_source_for_creation(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(\n                re.compile("action=torrent"),\n                [\