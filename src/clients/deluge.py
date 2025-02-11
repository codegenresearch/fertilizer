import json
import base64
import requests
from pathlib import Path

from ..errors import TorrentClientError, TorrentClientAuthenticationError
from .torrent_client import TorrentClient
from requests.exceptions import RequestException, HTTPError, Timeout
from requests.structures import CaseInsensitiveDict


class Deluge(TorrentClient):
    ERROR_CODES = {
        "AUTH_FAILED": "Failed to authenticate with Deluge",
        "AUTH_INCORRECT_PASSWORD": "Authentication failed: Incorrect password",
        "AUTH_SESSION_EXPIRED": "Authentication failed: Session expired",
        "AUTH_NETWORK_ERROR": "Authentication failed: Network error",
        "METHOD_ERROR": "Deluge method returned an error",
        "TIMEOUT_ERROR": "Deluge method timed out after 10 seconds",
    }

    def __init__(self, rpc_url):
        super().__init__()
        self._rpc_url = rpc_url
        self._deluge_cookie = None
        self._deluge_request_id = 0
        self._label_plugin_enabled = False

    def setup(self):
        """Set up the Deluge client by authenticating and checking label plugin status."""
        connection_response = self.__authenticate()
        self._label_plugin_enabled = self.__is_label_plugin_enabled()
        return connection_response

    def get_torrent_info(self, infohash):
        """Retrieve information about a torrent by its infohash."""
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

        response = self.__wrap_request("web.update_ui", params)
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
        """Inject a new torrent into Deluge based on a source torrent's infohash."""
        source_torrent_info = self.get_torrent_info(source_torrent_infohash)

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

        new_torrent_infohash = self.__wrap_request("core.add_torrent_file", params)
        newtorrent_label = self.__determine_label(source_torrent_info)
        return self.__set_label(new_torrent_infohash, newtorrent_label)

    def __authenticate(self):
        """Authenticate with the Deluge RPC server."""
        _href, _username, password = self._extract_credentials_from_url(self._rpc_url)
        if not password:
            raise Exception("You need to define a password in the Deluge RPC URL. (e.g. http://:<PASSWORD>@localhost:8112)")

        try:
            auth_response = self.__request("auth.login", [password])
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_INCORRECT_PASSWORD"])
            raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_NETWORK_ERROR"])
        except Timeout:
            raise TorrentClientAuthenticationError(self.ERROR_CODES["TIMEOUT_ERROR"])
        except RequestException as network_error:
            raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_NETWORK_ERROR"]) from network_error

        if not auth_response:
            raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_FAILED"])

        try:
            return self.__request("web.connected")
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_SESSION_EXPIRED"])
            raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_NETWORK_ERROR"])
        except Timeout:
            raise TorrentClientAuthenticationError(self.ERROR_CODES["TIMEOUT_ERROR"])
        except RequestException as network_error:
            raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_NETWORK_ERROR"]) from network_error

    def __is_label_plugin_enabled(self):
        """Check if the label plugin is enabled in Deluge."""
        response = self.__wrap_request("core.get_enabled_plugins")
        return "Label" in response

    def __determine_label(self, torrent_info):
        """Determine the label for a new torrent based on the source torrent's label."""
        current_label = torrent_info.get("label")

        if not current_label or current_label == self.torrent_label:
            return self.torrent_label

        return f"{current_label}.{self.torrent_label}"

    def __set_label(self, infohash, label):
        """Set a label for a torrent in Deluge."""
        if not self._label_plugin_enabled:
            return

        current_labels = self.__wrap_request("label.get_labels")
        if label not in current_labels:
            self.__wrap_request("label.add", [label])

        return self.__wrap_request("label.set_torrent", [infohash, label])

    def __wrap_request(self, method, params=[]):
        """Wrap the request method to handle re-authentication if necessary."""
        try:
            return self.__request(method, params)
        except TorrentClientAuthenticationError:
            self.__authenticate()
            return self.__request(method, params)

    def __request(self, method, params=[]):
        """Send a request to the Deluge RPC server."""
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
            raise TorrentClientError(self.ERROR_CODES["TIMEOUT_ERROR"])
        except HTTPError as http_error:
            if http_error.response.status_code == 401:
                raise TorrentClientAuthenticationError(self.ERROR_CODES["AUTH_SESSION_EXPIRED"])
            elif http_error.response.status_code == 408:
                raise TorrentClientError(self.ERROR_CODES["TIMEOUT_ERROR"])
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
        """Handle response headers to update the Deluge cookie."""
        if "Set-Cookie" in headers:
            self._deluge_cookie = headers["Set-Cookie"].split(";")[0]


This code addresses the feedback by:
1. Removing the misplaced text causing the `SyntaxError`.
2. Changing the `ERROR_CODES` dictionary to use string keys.
3. Ensuring the `__authenticate` method directly calls the `__request` method to avoid potential infinite loops.
4. Ensuring the `__set_label` method returns the result of the last `__wrap_request` call.
5. Refining error handling in the `__request` method to specifically check for timeout errors (HTTP status code 408).
6. Adding docstrings to methods for better documentation.
7. Maintaining consistent indentation and spacing.
8. Ensuring method calls avoid potential infinite loops, especially in the context of authentication.