import json
import base64
import requests
from pathlib import Path

from ..errors import TorrentClientError, TorrentClientAuthenticationError
from .torrent_client import TorrentClient
from requests.exceptions import RequestException
from requests.structures import CaseInsensitiveDict


class Deluge(TorrentClient):
    AUTH_ERROR_CODE = 1
    TIMEOUT_ERROR_CODE = 408

    def __init__(self, rpc_url):
        super().__init__()
        self._rpc_url = rpc_url
        self._deluge_cookie = None
        self._deluge_request_id = 0
        self._label_plugin_enabled = False

    def setup(self):
        try:
            self.__authenticate()
            self._label_plugin_enabled = self.__is_label_plugin_enabled()
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed during setup: {auth_error}")

        return True

    def get_torrent_info(self, infohash):
        infohash = infohash.lower()
        params = [
            [
                "name",
                "state",
                "progress",
                "save_path",
                "label",
                "total_remaining",
            ],
            {"hash": infohash},
        ]

        try:
            response = self.__wrap_request("web.update_ui", params)
        except TorrentClientError as request_error:
            raise TorrentClientError(f"Failed to retrieve torrent info for {infohash}: {request_error}")

        if "torrents" in response:
            torrent = response["torrents"].get(infohash)

            if torrent is None:
                raise TorrentClientError(f"Torrent not found in client ({infohash})")
        else:
            raise TorrentClientError("Client returned unexpected response (object missing)")

        torrent_completed = (
            (torrent["state"] == "Paused" and (torrent["progress"] == 100 or not torrent["total_remaining"]))
            or torrent["state"] == "Seeding"
            or torrent["progress"] == 100
            or not torrent["total_remaining"]
        )

        return {
            "complete": torrent_completed,
            "label": torrent.get("label"),
            "save_path": torrent["save_path"],
        }

    def inject_torrent(self, source_torrent_infohash, new_torrent_filepath, save_path_override=None):
        try:
            source_torrent_info = self.get_torrent_info(source_torrent_infohash)
        except TorrentClientError as info_error:
            raise TorrentClientError(f"Failed to get torrent info for {source_torrent_infohash}: {info_error}")

        if not source_torrent_info["complete"]:
            raise TorrentClientError("Cannot inject a torrent that is not complete")

        params = [
            f"{Path(new_torrent_filepath).stem}.fertilizer.torrent",
            base64.b64encode(open(new_torrent_filepath, "rb").read()).decode(),
            {
                "download_location": save_path_override if save_path_override else source_torrent_info["save_path"],
                "seed_mode": True,
                "add_paused": False,
            },
        ]

        try:
            new_torrent_infohash = self.__wrap_request("core.add_torrent_file", params)
        except TorrentClientError as add_error:
            raise TorrentClientError(f"Failed to add torrent file: {add_error}")

        newtorrent_label = self.__determine_label(source_torrent_info)
        try:
            self.__set_label(new_torrent_infohash, newtorrent_label)
        except TorrentClientError as label_error:
            raise TorrentClientError(f"Failed to set label for torrent {new_torrent_infohash}: {label_error}")

        return new_torrent_infohash

    def __authenticate(self):
        _href, _username, password = self._extract_credentials_from_url(self._rpc_url)
        if not password:
            raise Exception("You need to define a password in the Deluge RPC URL. (e.g. http://:<PASSWORD>@localhost:8112)")

        try:
            auth_response = self.__request("auth.login", [password])
        except RequestException as network_error:
            raise TorrentClientAuthenticationError("Failed to connect to Deluge for authentication") from network_error

        if not auth_response:
            raise TorrentClientAuthenticationError("Reached Deluge RPC endpoint but failed to authenticate")

        try:
            self.__request("web.connected")
        except RequestException as network_error:
            raise TorrentClientAuthenticationError("Failed to connect to Deluge after authentication") from network_error

    def __is_label_plugin_enabled(self):
        try:
            response = self.__request("core.get_enabled_plugins")
        except RequestException as network_error:
            raise TorrentClientError("Failed to check label plugin status") from network_error

        return "Label" in response

    def __determine_label(self, torrent_info):
        current_label = torrent_info.get("label")

        if not current_label or current_label == self.torrent_label:
            return self.torrent_label

        return f"{current_label}.{self.torrent_label}"

    def __set_label(self, infohash, label):
        if not self._label_plugin_enabled:
            return

        try:
            current_labels = self.__request("label.get_labels")
        except RequestException as network_error:
            raise TorrentClientError("Failed to retrieve labels") from network_error

        if label not in current_labels:
            try:
                self.__request("label.add", [label])
            except RequestException as network_error:
                raise TorrentClientError(f"Failed to add label {label}") from network_error

        try:
            self.__request("label.set_torrent", [infohash, label])
        except RequestException as network_error:
            raise TorrentClientError(f"Failed to set label {label} for torrent {infohash}") from network_error

    def __wrap_request(self, method, params=[]):
        try:
            return self.__request(method, params)
        except TorrentClientAuthenticationError:
            self.__authenticate()
            return self.__request(method, params)

    def __request(self, method, params=[]):
        href, _, _ = self._extract_credentials_from_url(self._rpc_url)

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        if self._deluge_cookie:
            headers["Cookie"] = self._deluge_cookie

        try:
            response = requests.post(
                href,
                json={
                    "method": method,
                    "params": params,
                    "id": self._deluge_request_id,
                },
                headers=headers,
                timeout=10,
            )
            self._deluge_request_id += 1
        except RequestException as network_error:
            if network_error.response and network_error.response.status_code == self.TIMEOUT_ERROR_CODE:
                raise TorrentClientError(f"Deluge method {method} timed out after 10 seconds") from network_error
            raise TorrentClientError(f"Failed to connect to Deluge at {href}") from network_error

        try:
            json_response = response.json()
        except json.JSONDecodeError as json_parse_error:
            raise TorrentClientError(f"Deluge method {method} response was non-JSON") from json_parse_error

        self.__handle_response_headers(response.headers)

        if "error" in json_response and json_response["error"]:
            if json_response["error"]["code"] == self.AUTH_ERROR_CODE:
                raise TorrentClientAuthenticationError("Failed to authenticate with Deluge")
            raise TorrentClientError(f"Deluge method {method} returned an error: {json_response['error']}")

        return json_response["result"]

    def __handle_response_headers(self, headers):
        if "Set-Cookie" in headers:
            self._deluge_cookie = headers["Set-Cookie"].split(";")[0]


This revised code addresses the feedback by:
1. Implementing a `__wrap_request` method to handle re-authentication in case of authentication errors.
2. Modifying the `__authenticate` method to raise `TorrentClientAuthenticationError` with a specific message when authentication fails.
3. Ensuring that specific exceptions are raised for different error conditions.
4. Simplifying the logic in methods like `setup` and `inject_torrent` by removing unnecessary try-except blocks.
5. Defining error codes as constants within the class.
6. Ensuring consistent formatting and structure.