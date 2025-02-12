import os
from urllib.parse import urlparse, unquote

from src.filesystem import sane_join
from src.clients.qbittorrent import Qbittorrent  # Assuming Qbittorrent is a concrete implementation of TorrentClient

class TorrentClient:
    def __init__(self):
        self.torrent_label = "fertilizer"

    def setup(self):
        raise NotImplementedError

    def get_torrent_info(self, infohash):
        raise NotImplementedError

    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):
        raise NotImplementedError

    def _extract_credentials_from_url(self, url, base_path=None):
        parsed_url = urlparse(url)
        username = unquote(parsed_url.username) if parsed_url.username else ""
        password = unquote(parsed_url.password) if parsed_url.password else ""
        origin = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}"

        if base_path is not None:
            href = sane_join(origin, os.path.normpath(base_path))
        else:
            href = sane_join(origin, (parsed_url.path if parsed_url.path != "/" else ""))

        return href, username, password

    def _determine_label(self, torrent_info):
        current_label = torrent_info.get("label")

        if not current_label:
            return self.torrent_label

        if current_label == self.torrent_label or current_label.endswith(f".{self.torrent_label}"):
            return current_label

        return f"{current_label}.{self.torrent_label}"

    def list_torrents(self):
        """List all torrents in the client."""
        raise NotImplementedError

    def delete_torrent(self, infohash):
        """Delete a torrent by infohash."""
        raise NotImplementedError

class TestTorrentClient(TorrentClient):
    def __init__(self):
        super().__init__()
        self.torrents = {}

    def get_torrent_info(self, infohash):
        return self.torrents.get(infohash, {})

    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):
        new_torrent_infohash = "test_infohash"  # Simulate infohash calculation
        if new_torrent_infohash in self.torrents:
            raise TorrentExistsInClientError(f"New torrent already exists in client ({new_torrent_infohash})")
        self.torrents[new_torrent_infohash] = {
            "source_torrent_infohash": source_torrent_infohash,
            "new_torrent_filepath": new_torrent_filepath,
            "save_path_override": save_path_override
        }
        return new_torrent_infohash

    def list_torrents(self):
        return list(self.torrents.values())

    def delete_torrent(self, infohash):
        if infohash in self.torrents:
            del self.torrents[infohash]
        else:
            raise TorrentClientError(f"Torrent not found in client ({infohash})")

# Example of using Qbittorrent as a concrete implementation
class ConcreteQbittorrentClient(Qbittorrent):
    def __init__(self, qbit_url):
        super().__init__(qbit_url)
        self.torrent_label = "fertilizer"  # Override if needed

    def list_torrents(self):
        response = self.__wrap_request("torrents/info")
        if response:
            return json.loads(response)
        raise TorrentClientError("Failed to retrieve torrents list")

    def delete_torrent(self, infohash):
        self.__wrap_request("torrents/delete", data={"hashes": infohash})