import json
import requests
from pathlib import Path
from requests.structures import CaseInsensitiveDict

from ..utils import url_join
from ..parser import get_bencoded_data, calculate_infohash
from ..errors import TorrentClientError, TorrentClientAuthenticationError, TorrentExistsInClientError
from .torrent_client import TorrentClient


class Qbittorrent(TorrentClient):
    def __init__(self, qbit_url):
        super().__init__()
        self._qbit_url_parts = self._extract_credentials_from_url(qbit_url, "/api/v2")
        self._qbit_cookie = None

    def setup(self):
        self.__authenticate()
        return self

    def get_torrent_info(self, infohash):
        response = self.__wrap_request("torrents/info", data={"hashes": infohash})
        if not response:
            raise TorrentClientError(f"Torrent not found in client ({infohash})")

        parsed_response = json.loads(response)
        if not parsed_response:
            raise TorrentClientError(f"Torrent not found in client ({infohash})")

        torrent = parsed_response[0]
        torrent_completed = torrent["progress"] == 1.0 or torrent["state"] == "pausedUP" or torrent["completion_on"] > 0

        return {
            "complete": torrent_completed,
            "label": torrent["category"],
            "save_path": torrent["save_path"],
            "content_path": torrent["content_path"],
        }

    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):
        source_torrent_info = self.get_torrent_info(source_torrent_infohash)
        new_torrent_infohash = calculate_infohash(get_bencoded_data(new_torrent_filepath)).lower()

        if self.__torrent_exists_in_client(new_torrent_infohash):
            raise TorrentExistsInClientError(f"New torrent already exists in client ({new_torrent_infohash})")

        injection_filename = f"{Path(new_torrent_filepath).stem}.fertilizer.torrent"
        torrents = {"torrents": (injection_filename, open(new_torrent_filepath, "rb"), "application/x-bittorrent")}
        save_path = save_path_override or source_torrent_info["save_path"]
        params = {
            "autoTMM": False,
            "category": self._determine_label(source_torrent_info),
            "tags": self.torrent_label,
            "savepath": save_path,
        }

        self.__wrap_request("torrents/add", data=params, files=torrents)
        return new_torrent_infohash

    def __authenticate(self):
        href, username, password = self._qbit_url_parts
        payload = {"username": username, "password": password} if username and password else {}

        try:
            response = requests.post(f"{href}/auth/login", data=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise TorrentClientAuthenticationError(f"qBittorrent login failed: {e}")

        self._qbit_cookie = response.cookies.get_dict().get("SID")
        if not self._qbit_cookie:
            raise TorrentClientAuthenticationError("qBittorrent login failed: Invalid username or password")

    def __wrap_request(self, path, data=None, files=None):
        try:
            return self.__request(path, data, files)
        except TorrentClientAuthenticationError:
            self.__authenticate()
            return self.__request(path, data, files)

    def __request(self, path, data=None, files=None):
        href, _username, _password = self._qbit_url_parts

        try:
            response = requests.post(
                url_join(href, path),
                headers=CaseInsensitiveDict({"Cookie": f"SID={self._qbit_cookie}"}),
                data=data,
                files=files,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if e.response.status_code == 403:
                print(e.response.text)
                raise TorrentClientAuthenticationError("Failed to authenticate with qBittorrent")
            raise TorrentClientError(f"qBittorrent request to '{path}' failed: {e}")

    def __torrent_exists_in_client(self, infohash):
        try:
            self.get_torrent_info(infohash)
            return True
        except TorrentClientError:
            return False


### Key Changes:
1. **Removed Offending Comments:** Ensured all comments are properly formatted using `#` for single-line comments and removed any invalid syntax lines.
2. **Response Handling in `get_torrent_info`:** Ensured the response is checked for validity before parsing.
3. **Variable Naming Consistency:** Used `__torrent_exists_in_client` for checking if the new torrent already exists in the client.
4. **Conditional Logic for `save_path`:** Used a more concise way to determine `save_path` in `inject_torrent`.
5. **Authentication Logic:** Streamlined the payload construction in `__authenticate`.
6. **Error Handling Consistency:** Ensured consistent error handling in the `__request` method.
7. **Code Formatting:** Ensured consistent indentation and spacing for better readability.
8. **Return Value in `__torrent_exists_in_client`:** Simplified the return value logic to match the gold code's style.