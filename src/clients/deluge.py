import json\nimport base64\nimport requests\nfrom pathlib import Path\n\nfrom ..errors import TorrentClientError, TorrentClientAuthenticationError\nfrom .torrent_client import TorrentClient\nfrom requests.exceptions import RequestException, HTTPError\nfrom requests.structures import CaseInsensitiveDict\n\n\nclass Deluge(TorrentClient):\n    def __init__(self, rpc_url):\n        super().__init__()\n        self._rpc_url = rpc_url\n        self._deluge_cookie = None\n        self._deluge_request_id = 0\n        self._label_plugin_enabled = False\n\n    def setup(self):\n        connection_response = self.__authenticate()\n        self._label_plugin_enabled = self.__is_label_plugin_enabled()\n\n        return connection_response\n\n    def get_torrent_info(self, infohash):\n        infohash = infohash.lower()\n        params = [\n            [\n                "name",\n                "state",\n                "progress",\n                "save_path",\n                "label",\n                "total_remaining",\n            ],\n            {"hash": infohash},\n        ]\n\n        response = self.__request("web.update_ui", params)\n        if "torrents" in response:\n            torrent = response["torrents"].get(infohash)\n\n            if torrent is None:\n                raise TorrentClientError(f"Torrent not found in client ({infohash})")\n        else:\n            raise TorrentClientError("Client returned unexpected response (object missing)")\n\n        torrent_completed = (\n            (torrent["state"] == "Paused" and (torrent["progress"] == 100 or not torrent["total_remaining"]))\n            or torrent["state"] == "Seeding"\n            or torrent["progress"] == 100\n            or not torrent["total_remaining"]\n        )\n\n        return {\n            "complete": torrent_completed,\n            "label": torrent.get("label"),\n            "save_path": torrent["save_path"],\n        }\n\n    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):\n        source_torrent_info = self.get_torrent_info(source_torrent_infohash)\n\n        if not source_torrent_info["complete"]:\n            raise TorrentClientError("Cannot inject a torrent that is not complete")\n\n        params = [\n            f"{Path(new_torrent_filepath).stem}.fertilizer.torrent",\n            base64.b64encode(open(new_torrent_filepath, "rb").read()).decode(),\n            {\n                "download_location": save_path_override if save_path_override else source_torrent_info["save_path"],\n                "seed_mode": True,\n                "add_paused": False,\n            },\n        ]\n\n        new_torrent_infohash = self.__request("core.add_torrent_file", params)\n        newtorrent_label = self.__determine_label(source_torrent_info)\n        self.__set_label(new_torrent_infohash, newtorrent_label)\n\n        return new_torrent_infohash\n\n    def __authenticate(self):\n        _href, _username, password = self._extract_credentials_from_url(self._rpc_url)\n        if not password:\n            raise Exception("You need to define a password in the Deluge RPC URL. (e.g. http://:<PASSWORD>@localhost:8112)")\n\n        auth_response = self.__wrap_request("auth.login", [password])\n        if not auth_response:\n            raise TorrentClientAuthenticationError("Failed to authenticate with Deluge")\n\n        return self.__wrap_request("web.connected")\n\n    def __is_label_plugin_enabled(self):\n        response = self.__request("core.get_enabled_plugins")\n\n        return "Label" in response\n\n    def __determine_label(self, torrent_info):\n        current_label = torrent_info.get("label")\n\n        if not current_label or current_label == self.torrent_label:\n            return self.torrent_label\n\n        return f"{current_label}.{self.torrent_label}"\n\n    def __set_label(self, infohash, label):\n        if not self._label_plugin_enabled:\n            return\n\n        current_labels = self.__request("label.get_labels")\n        if label not in current_labels:\n            self.__request("label.add", [label])\n\n        return self.__request("label.set_torrent", [infohash, label])\n\n    def __request(self, method, params=[]):\n        href, _, _ = self._extract_credentials_from_url(self._rpc_url)\n\n        headers = CaseInsensitiveDict()\n        headers["Content-Type"] = "application/json"\n        if self._deluge_cookie:\n            headers["Cookie"] = self._deluge_cookie\n\n        try:\n            response = requests.post(\n                href,\n                json={\n                    "method": method,\n                    "params": params,\n                    "id": self._deluge_request_id,\n                },\n                headers=headers,\n                timeout=10,\n            )\n            self._deluge_request_id += 1\n        except HTTPError as http_error:\n            if http_error.response.status_code == 408:\n                raise TorrentClientError(f"Deluge method {method} timed out after 10 seconds")\n            raise TorrentClientError(f"Failed to connect to Deluge at {href}") from http_error\n        except RequestException as network_error:\n            raise TorrentClientError(f"Failed to connect to Deluge at {href}") from network_error\n\n        try:\n            json_response = response.json()\n        except json.JSONDecodeError as json_parse_error:\n            raise TorrentClientError(f"Deluge method {method} response was non-JSON") from json_parse_error\n\n        self.__handle_response_headers(response.headers)\n\n        if "error" in json_response and json_response["error"]:\n            raise TorrentClientError(f"Deluge method {method} returned an error: {json_response['error']}")\n\n        return json_response["result"]\n\n    def __wrap_request(self, method, params=[]):\n        try:\n            return self.__request(method, params)\n        except TorrentClientAuthenticationError:\n            self.__authenticate()\n            return self.__request(method, params)\n\n    def __handle_response_headers(self, headers):\n        if "Set-Cookie" in headers:\n            self._deluge_cookie = headers["Set-Cookie"].split(";")[0]\n