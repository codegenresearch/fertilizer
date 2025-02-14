import sys
from time import sleep

from colorama import Fore

class ErrorHandler:
    def __init__(self):
        self.error_codes = {
            "AUTHENTICATION_ERROR": "Authentication failed",
            "REQUEST_ERROR": "Request failed",
            "JSON_DECODING_ERROR": "JSON decoding error",
            "TIMEOUT_ERROR": "Request timed out",
            "CONNECTION_ERROR": "Unable to connect",
            "UNKNOWN_TRACKER_ERROR": "Unknown tracker error",
            "TORRENT_NOT_FOUND_ERROR": "Torrent not found",
            "TORRENT_ALREADY_EXISTS_ERROR": "Torrent already exists",
            "CONFIG_KEY_ERROR": "Configuration key error",
            "TORRENT_CLIENT_ERROR": "Torrent client error",
            "TORRENT_INJECTION_ERROR": "Torrent injection error"
        }

    def handle_error(
        self,
        error_code: str,
        exception_details: (str | None) = None,
        wait_time: int = 0,
        extra_description: str = "",
        should_exit: bool = False,
    ) -> None:
        action = "Exiting" if should_exit else "Retrying"
        action += f" in {wait_time} seconds..." if wait_time else "..."
        exception_message = f"\n{Fore.LIGHTBLACK_EX}{exception_details}" if exception_details is not None else ""

        error_description = self.error_codes.get(error_code, "An error occurred")
        print(f"{Fore.RED}{error_description}: {extra_description}. {action}{exception_message}{Fore.RESET}")
        sleep(wait_time)

        if should_exit:
            sys.exit(1)


class AuthenticationError(Exception):
    pass


class TorrentDecodingError(Exception):
    pass


class UnknownTrackerError(Exception):
    pass


class TorrentNotFoundError(Exception):
    pass


class TorrentAlreadyExistsError(Exception):
    pass


class ConfigKeyError(Exception):
    pass


class TorrentClientError(Exception):
    pass


class TorrentInjectionError(Exception):
    pass