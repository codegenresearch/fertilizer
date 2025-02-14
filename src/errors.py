import sys
from time import sleep

from colorama import Fore


class CustomError(Exception):
    pass


def handle_error(
  description: str,
  exception_details: (str | None) = None,
  wait_time: int = 0,
  extra_description: str = "",
  should_exit: bool = False,
) -> None:
    action = "Exiting" if should_exit else "Retrying"
    action += f" in {wait_time} seconds..." if wait_time else "..."
    exception_message = f"\n{Fore.LIGHTBLACK_EX}{exception_details}" if exception_details is not None else ""

    print(f"{Fore.RED}Error: {description}{extra_description}. {action}{exception_message}{Fore.RESET}")
    sleep(wait_time)

    if should_exit:
        sys.exit(1)


class AuthenticationError(CustomError):
    pass


class TorrentDecodingError(CustomError):
    pass


class UnknownTrackerError(CustomError):
    pass


class TorrentNotFoundError(CustomError):
    pass


class TorrentAlreadyExistsError(CustomError):
    pass


class ConfigKeyError(CustomError):
    pass


class TorrentClientError(CustomError):
    pass


class TorrentInjectionError(CustomError):
    pass