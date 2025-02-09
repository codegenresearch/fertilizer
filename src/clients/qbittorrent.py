import json\nimport requests\nfrom pathlib import Path\nfrom requests.structures import CaseInsensitiveDict\n\nfrom ..filesystem import url_join\nfrom ..parser import get_bencoded_data, calculate_infohash\nfrom ..errors import TorrentClientError, TorrentClientAuthenticationError, TorrentExistsInClientError\nfrom .torrent_client import TorrentClient\n\n\nclass Qbittorrent(TorrentClient):\n    def __init__(self, qbit_url):\n        super().__init__()\n        self._qbit_url_parts = self._extract_credentials_from_url(qbit_url, "/api/v2")\n        self._qbit_cookie = None\n\n    def setup(self):\n        self.__authenticate()\n        return self\n\n    def get_torrent_info(self, infohash):\n        response = self.__wrap_request("torrents/info", data={"hashes": infohash})\n        if not response:\n            raise TorrentClientError("Client returned unexpected response")\n\n        try:\n            parsed_response = json.loads(response)\n        except json.JSONDecodeError:\n            raise TorrentClientError("Failed to parse JSON response")\n\n        if not parsed_response:\n            raise TorrentClientError(f"Torrent not found in client ({infohash})")\n\n        torrent = parsed_response[0]\n        torrent_completed = torrent["progress"] == 1.0 or torrent["state"] == "pausedUP" or torrent["completion_on"] > 0\n\n        return {\n            "complete": torrent_completed,\n            "label": torrent["category"],\n            "save_path": torrent["save_path"],\n            "content_path": torrent["content_path"],\n        }\n\n    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):\n        source_torrent_info = self.get_torrent_info(source_torrent_infohash)\n        new_torrent_infohash = calculate_infohash(get_bencoded_data(new_torrent_filepath)).lower()\n        new_torrent_already_exists = self.__does_torrent_exist_in_client(new_torrent_infohash)\n\n        if new_torrent_already_exists:\n            raise TorrentExistsInClientError(f"New torrent already exists in client ({new_torrent_infohash})")\n\n        injection_filename = f"{Path(new_torrent_filepath).stem}.fertilizer.torrent"\n        torrents = {"torrents": (injection_filename, open(new_torrent_filepath, "rb"), "application/x-bittorrent")}\n        params = {\n            "autoTMM": False,\n            "category": self._determine_label(source_torrent_info),\n            "tags": self.torrent_label,\n            "savepath": save_path_override if save_path_override else source_torrent_info["save_path"],\n        }\n\n        self.__wrap_request("torrents/add", data=params, files=torrents)\n        return new_torrent_infohash\n\n    def __authenticate(self):\n        # This method specifically does not use the __wrap_request method\n        # because we want to avoid an infinite loop of re-authenticating\n        href, username, password = self._qbit_url_parts\n        payload = {"username": username, "password": password} if username or password else {}\n\n        try:\n            response = requests.post(f"{href}/auth/login", data=payload)\n            response.raise_for_status()\n        except requests.RequestException as e:\n            raise TorrentClientAuthenticationError(f"qBittorrent login failed: {e}")\n\n        self._qbit_cookie = response.cookies.get_dict().get("SID")\n        if not self._qbit_cookie:\n            raise TorrentClientAuthenticationError("qBittorrent login failed: Invalid username or password")\n\n    def __wrap_request(self, path, data=None, files=None):\n        try:\n            return self.__request(path, data, files)\n        except TorrentClientAuthenticationError:\n            self.__authenticate()\n            return self.__request(path, data, files)\n\n    def __request(self, path, data=None, files=None):\n        href, _, _ = self._qbit_url_parts\n\n        try:\n            response = requests.post(\n                url_join(href, path),\n                headers=CaseInsensitiveDict({"Cookie": f"SID={self._qbit_cookie}"}),\n                data=data,\n                files=files,\n            )\n            response.raise_for_status()\n            return response.text\n        except requests.RequestException as e:\n            if e.response.status_code == 403:\n                print(e.response.text)\n                raise TorrentClientAuthenticationError("Failed to authenticate with qBittorrent")\n            raise TorrentClientError(f"qBittorrent request to '{path}' failed: {e}")\n\n    def __does_torrent_exist_in_client(self, infohash):\n        return bool(self.get_torrent_info(infohash))\n