import os\nimport re\nimport pytest\nimport requests_mock\n\nfrom .helpers import get_torrent_path, SetupTeardown\nfrom src.trackers import RedTracker, OpsTracker\nfrom src.parser import get_bencoded_data\nfrom src.errors import (\n    TorrentAlreadyExistsError,\n    TorrentDecodingError,\n    UnknownTrackerError,\n    TorrentNotFoundError,\n)\nfrom src.torrent import (\n    generate_new_torrent_from_file,\n    generate_torrent_output_filepath,\n)\n\n\nclass TestGenerateNewTorrentFromFile(SetupTeardown):\n    def test_saves_new_torrent_from_red_to_ops(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("red_source")\n            _, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n\n            assert os.path.isfile(filepath)\n            assert parsed_torrent[b"announce"] == b"https://home.opsfet.ch/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://orpheus.network/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"OPS"\n\n            os.remove(filepath)\n\n    def test_saves_new_torrent_from_ops_to_red(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("ops_source")\n            _, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n\n            os.remove(filepath)\n\n    def test_works_with_qbit_fastresume_files(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("qbit_ops")\n            _, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n\n            assert parsed_torrent[b"announce"] == b"https://flacsfor.me/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://redacted.ch/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"RED"\n\n            os.remove(filepath)\n\n    def test_returns_new_tracker_instance_and_filepath(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("ops_source")\n            new_tracker, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            get_bencoded_data(filepath)\n\n            assert os.path.isfile(filepath)\n            assert new_tracker == RedTracker\n\n            os.remove(filepath)\n\n    def test_raises_error_if_cannot_decode_torrent(self, red_api, ops_api):\n        with pytest.raises(TorrentDecodingError) as excinfo:\n            torrent_path = get_torrent_path("broken")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n\n        assert str(excinfo.value) == "Error decoding torrent file"\n\n    def test_raises_error_if_tracker_not_found(self, red_api, ops_api):\n        with pytest.raises(UnknownTrackerError) as excinfo:\n            torrent_path = get_torrent_path("no_source")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n\n        assert str(excinfo.value) == "Torrent not from OPS or RED based on source or announce URL"\n\n    def test_raises_error_if_infohash_found_in_input(self, red_api, ops_api):\n        input_hashes = {"2AEE440CDC7429B3E4A7E4D20E3839DBB48D72C2": "foo"}\n\n        with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n            torrent_path = get_torrent_path("red_source")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api, input_hashes)\n\n        assert str(excinfo.value) == "Torrent already exists in input directory as foo"\n\n    def test_raises_error_if_infohash_found_in_output(self, red_api, ops_api):\n        output_hashes = {"2AEE440CDC7429B3E4A7E4D20E3839DBB48D72C2": "bar"}\n\n        with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n            torrent_path = get_torrent_path("red_source")\n            generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api, {}, output_hashes)\n\n        assert str(excinfo.value) == "Torrent already exists in output directory as bar"\n\n    def test_raises_error_if_torrent_already_exists(self, red_api, ops_api):\n        filepath = generate_torrent_output_filepath(self.TORRENT_SUCCESS_RESPONSE, OpsTracker(), "/tmp")\n\n        os.makedirs(os.path.dirname(filepath), exist_ok=True)\n        with open(filepath, "w") as f:\n            f.write("")\n\n        with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n            with requests_mock.Mocker() as m:\n                m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n                m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n\n        assert str(excinfo.value) == f"Torrent file already exists at {filepath}"\n        os.remove(filepath)\n\n    def test_raises_error_if_api_response_error(self, red_api, ops_api):\n        with pytest.raises(TorrentNotFoundError) as excinfo:\n            with requests_mock.Mocker() as m:\n                m.get(re.compile(r"action=torrent"), json=self.TORRENT_KNOWN_BAD_RESPONSE)\n                m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n\n        assert str(excinfo.value) == "Torrent could not be found on OPS"\n\n    def test_raises_error_if_api_response_unknown(self, red_api, ops_api):\n        with pytest.raises(Exception) as excinfo:\n            with requests_mock.Mocker() as m:\n                m.get(re.compile(r"action=torrent"), json=self.TORRENT_UNKNOWN_BAD_RESPONSE)\n                m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n                torrent_path = get_torrent_path("red_source")\n                generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n\n        assert str(excinfo.value) == "An unknown error occurred in the API response from OPS"\n\n    def test_handles_alternate_source_flags(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("red_source")\n            _, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n\n            assert parsed_torrent[b"announce"] == b"https://home.opsfet.ch/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://orpheus.network/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"OPS"\n\n            os.remove(filepath)\n\n    def test_handles_blank_source_flags(self, red_api, ops_api):\n        with requests_mock.Mocker() as m:\n            m.get(re.compile(r"action=torrent"), json=self.TORRENT_SUCCESS_RESPONSE)\n            m.get(re.compile(r"action=index"), json=self.ANNOUNCE_SUCCESS_RESPONSE)\n\n            torrent_path = get_torrent_path("red_source")\n            _, filepath = generate_new_torrent_from_file(torrent_path, "/tmp", red_api, ops_api)\n            parsed_torrent = get_bencoded_data(filepath)\n\n            assert parsed_torrent[b"announce"] == b"https://home.opsfet.ch/bar/announce"\n            assert parsed_torrent[b"comment"] == b"https://orpheus.network/torrents.php?torrentid=123"\n            assert parsed_torrent[b"info"][b"source"] == b"OPS"\n\n            os.remove(filepath)\n\n\nclass TestGenerateTorrentOutputFilepath(SetupTeardown):\n    API_RESPONSE = {"response": {"torrent": {"filePath": "foo"}}}\n\n    def test_constructs_a_path_from_response_and_source(self):\n        filepath = generate_torrent_output_filepath(self.API_RESPONSE, OpsTracker(), "base/dir")\n\n        assert filepath == "base/dir/OPS/foo [OPS].torrent"\n\n    def test_raises_error_if_file_exists(self):\n        filepath = generate_torrent_output_filepath(self.API_RESPONSE, OpsTracker(), "/tmp")\n\n        os.makedirs(os.path.dirname(filepath), exist_ok=True)\n        with open(filepath, "w") as f:\n            f.write("")\n\n        with pytest.raises(TorrentAlreadyExistsError) as excinfo:\n            generate_torrent_output_filepath(self.API_RESPONSE, OpsTracker(), "/tmp")\n\n        assert str(excinfo.value) == f"Torrent file already exists at {filepath}"\n        os.remove(filepath)\n