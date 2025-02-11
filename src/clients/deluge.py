import json
import base64
import requests
from pathlib import Path

from ..errors import TorrentClientError, TorrentClientAuthenticationError
from .torrent_client import TorrentClient
from requests.exceptions import RequestException, HTTPError, Timeout
from requests.structures import CaseInsensitiveDict


class Deluge(TorrentClient):
    def __init__(self, rpc_url):
        super().__init__()
        self._rpc_url = rpc_url
        self._deluge_cookie = None
        self._deluge_request_id = 0
        self._label_plugin_enabled = False

    def setup(self):
        try:
            connection_response = self.__authenticate()
            self._label_plugin_enabled = self.__is_label_plugin_enabled()
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed during setup: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Setup failed: {client_error}")

        return connection_response

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
            response = self.__request("web.update_ui", params)
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while getting torrent info: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to get torrent info: {client_error}")

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
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while injecting torrent: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to get source torrent info: {client_error}")

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
            new_torrent_infohash = self.__request("core.add_torrent_file", params)
            newtorrent_label = self.__determine_label(source_torrent_info)
            self.__set_label(new_torrent_infohash, newtorrent_label)
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while injecting torrent: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to inject torrent: {client_error}")

        return new_torrent_infohash

    def __authenticate(self):
        _href, _username, password = self._extract_credentials_from_url(self._rpc_url)
        if not password:
            raise Exception("You need to define a password in the Deluge RPC URL. (e.g. http://:<PASSWORD>@localhost:8112)")

        try:
            auth_response = self.__request("auth.login", [password])
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError("Authentication failed: Incorrect password")
            raise TorrentClientAuthenticationError(f"Authentication failed with HTTP error: {http_error}")
        except Timeout:
            raise TorrentClientAuthenticationError("Authentication request timed out")
        except RequestException as network_error:
            raise TorrentClientAuthenticationError(f"Network error during authentication: {network_error}")

        if not auth_response:
            raise TorrentClientAuthenticationError("Reached Deluge RPC endpoint but failed to authenticate")

        try:
            return self.__request("web.connected")
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError("Authentication failed: Session expired")
            raise TorrentClientAuthenticationError(f"Authentication failed with HTTP error: {http_error}")
        except Timeout:
            raise TorrentClientAuthenticationError("Connection check request timed out")
        except RequestException as network_error:
            raise TorrentClientAuthenticationError(f"Network error during connection check: {network_error}")

    def __is_label_plugin_enabled(self):
        try:
            response = self.__request("core.get_enabled_plugins")
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while checking label plugin: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to check label plugin: {client_error}")

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
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while setting label: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to get labels: {client_error}")

        if label not in current_labels:
            try:
                self.__request("label.add", [label])
            except TorrentClientAuthenticationError as auth_error:
                raise TorrentClientAuthenticationError(f"Authentication failed while adding label: {auth_error}")
            except TorrentClientError as client_error:
                raise TorrentClientError(f"Failed to add label: {client_error}")

        try:
            return self.__request("label.set_torrent", [infohash, label])
        except TorrentClientAuthenticationError as auth_error:
            raise TorrentClientAuthenticationError(f"Authentication failed while setting label: {auth_error}")
        except TorrentClientError as client_error:
            raise TorrentClientError(f"Failed to set label: {client_error}")

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
        except Timeout:
            raise TorrentClientError(f"Deluge method {method} timed out after 10 seconds")
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError(f"Authentication failed for method {method}")
            raise TorrentClientError(f"HTTP error during Deluge method {method}: {http_error}")
        except RequestException as network_error:
            raise TorrentClientError(f"Failed to connect to Deluge at {href}") from network_error

        try:
            json_response = response.json()
        except json.JSONDecodeError as json_parse_error:
            raise TorrentClientError(f"Deluge method {method} response was non-JSON") from json_parse_error

        self.__handle_response_headers(response.headers)

        if "error" in json_response and json_response["error"]:
            raise TorrentClientError(f"Deluge method {method} returned an error: {json_response['error']}")

        return json_response["result"]

    def __handle_response_headers(self, headers):
        if "Set-Cookie" in headers:
            self._deluge_cookie = headers["Set-Cookie"].split(";")[0]