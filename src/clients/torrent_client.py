import os
from urllib.parse import urlparse, unquote
from src.utils import url_join

class TorrentClient:
    def __init__(self):
        self.torrent_label = "fertilizer"

    def setup(self):
        raise NotImplementedError

    def get_torrent_info(self, *args, **kwargs):
        raise NotImplementedError

    def inject_torrent(self, *args, **kwargs):
        raise NotImplementedError

    def _extract_credentials_from_url(self, url, base_path=None):
        parsed_url = urlparse(url)
        username = unquote(parsed_url.username) if parsed_url.username else ""
        password = unquote(parsed_url.password) if parsed_url.password else ""
        origin = f"{parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}"

        if base_path:
            href = url_join(origin, os.path.normpath(base_path))
        else:
            href = url_join(origin, parsed_url.path if parsed_url.path != "/" else "")

        return href, username, password

    def _determine_label(self, torrent_info):
        current_label = torrent_info.get("label", "")
        if not current_label:
            return self.torrent_label
        if current_label == self.torrent_label or current_label.endswith(f".{self.torrent_label}"):
            return current_label
        return f"{current_label}.{self.torrent_label}"

    def list_torrents(self):
        """List all torrents in the client."""
        raise NotImplementedError

    def remove_torrent(self, infohash):
        """Remove a torrent from the client."""
        raise NotImplementedError

    def test_connection(self):
        """Test the connection to the torrent client."""
        try:
            self.get_torrent_info("dummy_infohash")
            return True
        except NotImplementedError:
            return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False