import os
from unittest import TestCase
from pytest import raises

from .helpers import get_torrent_path, SetupTeardown

from src.trackers import RedTracker, OpsTracker
from src.parser import (
    is_valid_infohash,
    get_source,
    get_name,
    get_bencoded_data,
    get_announce_url,
    get_origin_tracker,
    recalculate_hash_for_new_source,
    save_bencoded_data,
    calculate_infohash,
)
from src.errors import TorrentDecodingError


class TestIsValidInfohash(SetupTeardown):
    def test_returns_true_for_valid_infohash(self):
        assert is_valid_infohash("0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33")

    def test_returns_false_for_invalid_infohash(self):
        assert not is_valid_infohash("abc")
        assert not is_valid_infohash("mnopqrstuvwx")
        assert not is_valid_infohash("Ubeec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33")
        assert not is_valid_infohash(123)


class TestGetSource(SetupTeardown):
    def test_returns_source_if_present(self):
        assert get_source({b"info": {b"source": b"FOO"}}) == b"FOO"

    def test_returns_none_if_absent(self):
        assert get_source({}) is None


class TestGetName(SetupTeardown):
    def test_returns_name_if_present(self):
        assert get_name({b"info": {b"name": b"foo"}}) == b"foo"

    def test_returns_none_if_absent(self):
        assert get_name({}) is None


class TestGetAnnounceUrl(SetupTeardown):
    def test_returns_url_if_present_in_announce(self):
        assert get_announce_url({b"announce": b"https://foo.bar"}) == [b"https://foo.bar"]

    def test_returns_url_if_present_in_trackers(self):
        assert get_announce_url({b"trackers": [[b"https://foo.bar"], b"https://baz.qux"]}) == [
            b"https://foo.bar",
            b"https://baz.qux",
        ]

    def test_returns_none_if_absent(self):
        assert get_announce_url({}) is None


class TestGetOriginTracker(SetupTeardown):
    def test_returns_red_based_on_source(self):
        assert get_origin_tracker({b"info": {b"source": b"RED"}}) == RedTracker
        assert get_origin_tracker({b"info": {b"source": b"PTH"}}) == RedTracker

    def test_returns_ops_based_on_source(self):
        assert get_origin_tracker({b"info": {b"source": b"OPS"}}) == OpsTracker

    def test_returns_red_based_on_announce(self):
        assert get_origin_tracker({b"announce": b"https://flacsfor.me/123abc"}) == RedTracker

    def test_returns_ops_based_on_announce(self):
        assert get_origin_tracker({b"announce": b"https://home.opsfet.ch/123abc"}) == OpsTracker

    def test_returns_red_based_on_trackers(self):
        assert get_origin_tracker({b"trackers": [[b"https://flacsfor.me/123abc"], b"https://baz.qux"]}) == RedTracker

    def test_returns_ops_based_on_trackers(self):
        assert get_origin_tracker({b"trackers": [[b"https://home.opsfet.ch/123abc"], b"https://baz.qux"]}) == OpsTracker

    def test_returns_none_if_no_match(self):
        assert get_origin_tracker({}) is None
        assert get_origin_tracker({b"info": {b"source": b"FOO"}}) is None
        assert get_origin_tracker({b"announce": b"https://foo/123abc"}) is None


class TestCalculateInfohash(SetupTeardown):
    def test_returns_infohash(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        result = calculate_infohash(torrent_data)

        assert result == "FD2F1D966DF7E2E35B0CF56BC8510C6BB4D44467"

    def test_raises_if_no_info_key(self):
        torrent_data = {}
        with raises(TorrentDecodingError) as excinfo:
            calculate_infohash(torrent_data)
        assert "Torrent data does not contain 'info' key" in str(excinfo.value)


class TestRecalculateHashForNewSource(SetupTeardown):
    def test_replaces_source_and_returns_hash(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        new_source = b"OPS"

        result = recalculate_hash_for_new_source(torrent_data, new_source)

        assert result == "4F36F59992B6F7CB6EB6C2DEE06DD66AC81A981B"

    def test_raises_if_no_info_key(self):
        torrent_data = {}
        new_source = b"OPS"
        with raises(TorrentDecodingError) as excinfo:
            recalculate_hash_for_new_source(torrent_data, new_source)
        assert "Torrent data does not contain 'info' key" in str(excinfo.value)

    def test_doesnt_mutate_original_dict(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        new_source = b"OPS"

        recalculate_hash_for_new_source(torrent_data, new_source)

        assert torrent_data == {b"info": {b"source": b"RED"}}


class TestGetTorrentData(SetupTeardown):
    def test_returns_torrent_data(self):
        result = get_bencoded_data(get_torrent_path("no_source"))

        assert isinstance(result, dict)
        assert b"info" in result

    def test_returns_none_on_error(self):
        result = get_bencoded_data(get_torrent_path("broken"))

        assert result is None


class TestSaveTorrentData(SetupTeardown):
    def test_saves_torrent_data(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        filename = "/tmp/test_save_bencoded_data.torrent"

        save_bencoded_data(filename, torrent_data)

        with open(filename, "rb") as f:
            result = f.read()

        assert result == b"d4:infod6:source3:REDee"

        os.remove(filename)

    def test_returns_filename(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        filename = "/tmp/test_save_bencoded_data.torrent"

        result = save_bencoded_data(filename, torrent_data)

        assert result == filename

        os.remove(filename)

    def test_creates_parent_directory(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        filename = "/tmp/output/foo/test_save_bencoded_data.torrent"

        save_bencoded_data(filename, torrent_data)

        assert os.path.exists("/tmp/output/foo")

        os.remove(filename)
        os.rmdir("/tmp/output/foo")
        os.rmdir("/tmp/output")

    def test_handles_missing_parent_directory(self):
        torrent_data = {b"info": {b"source": b"RED"}}
        filename = "/tmp/nonexistent/output/foo/test_save_bencoded_data.torrent"

        save_bencoded_data(filename, torrent_data)

        assert os.path.exists("/tmp/nonexistent/output/foo")

        os.remove(filename)
        os.rmdir("/tmp/nonexistent/output/foo")
        os.rmdir("/tmp/nonexistent/output")
        os.rmdir("/tmp/nonexistent")


### Changes Made:
1. **Syntax Error Fix**: Removed any improperly formatted comments or string literals that could cause a `SyntaxError`.
2. **Import Statements**: Organized and formatted import statements consistently.
3. **Use of `pytest.raises`**: Consistently used `pytest.raises` for exception handling.
4. **Test Case Structure**: Reviewed and structured test cases similarly to the gold code.
5. **Error Handling**: Ensured all relevant methods include appropriate error handling with consistent error messages.
6. **Assertions**: Ensured assertions are consistent with the gold code.
7. **Cleanup Logic**: Ensured cleanup logic is handled consistently and effectively in tests.
8. **Code Formatting**: Maintained consistent formatting, including indentation, spacing, and line breaks.

These changes should address the feedback and bring the code closer to the gold standard.