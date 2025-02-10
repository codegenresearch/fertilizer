import os
from urllib.parse import urlparse, unquote

from src.utils import url_join


class TorrentClient:
    def __init__(self):
        self.torrent_label = "fertilizer"

    def setup(self):
        raise NotImplementedError

    def get_torrent_info(self, *_args, **_kwargs):
        raise NotImplementedError

    def inject_torrent(self, *_args, **_kwargs):
        raise NotImplementedError

    def _extract_credentials_from_url(self, url, base_path=None):
        parsed_url = urlparse(url)
        username = unquote(parsed_url.username) if parsed_url.username else ""
        password = unquote(parsed_url.password) if parsed_url.password else ""
        origin = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}"

        if base_path is not None:
            href = url_join(origin, os.path.normpath(base_path))
        else:
            href = url_join(origin, parsed_url.path)

        return href, username, password

    def _determine_label(self, torrent_info):
        current_label = torrent_info.get("label")

        if not current_label:
            return self.torrent_label

        if current_label == self.torrent_label or current_label.endswith(f".{self.torrent_label}"):
            return current_label

        return f"{current_label}.{self.torrent_label}"


class TestTorrentClient:
    def test_extract_credentials_from_url(self):
        url = "http://user:pass@localhost:8080/api/v2"
        expected_href = "http://localhost:8080/api/v2"
        expected_username = "user"
        expected_password = "pass"
        href, username, password = TorrentClient()._extract_credentials_from_url(url)
        assert href == expected_href
        assert username == expected_username
        assert password == expected_password

    def test_extract_credentials_from_url_no_credentials(self):
        url = "http://localhost:8080/api/v2"
        expected_href = "http://localhost:8080/api/v2"
        expected_username = ""
        expected_password = ""
        href, username, password = TorrentClient()._extract_credentials_from_url(url)
        assert href == expected_href
        assert username == expected_username
        assert password == expected_password

    def test_determine_label(self):
        torrent_info = {"label": "existing_label"}
        expected_label = "existing_label.fertilizer"
        label = TorrentClient()._determine_label(torrent_info)
        assert label == expected_label

    def test_determine_label_no_label(self):
        torrent_info = {}
        expected_label = "fertilizer"
        label = TorrentClient()._determine_label(torrent_info)
        assert label == expected_label

    def test_determine_label_with_fertilizer(self):
        torrent_info = {"label": "fertilizer"}
        expected_label = "fertilizer"
        label = TorrentClient()._determine_label(torrent_info)
        assert label == expected_label

    def test_determine_label_with_existing_fertilizer(self):
        torrent_info = {"label": "existing_label.fertilizer"}
        expected_label = "existing_label.fertilizer"
        label = TorrentClient()._determine_label(torrent_info)
        assert label == expected_label