import sys
from time import sleep

from colorama import Fore


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


def make_request(session, url, params, timeout, max_retries, retry_wait_time):
    current_retries = 1

    while current_retries <= max_retries:
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as e:
            err = "Request timed out", e
        except requests.exceptions.ConnectionError as e:
            err = "Unable to connect", e
        except requests.exceptions.RequestException as e:
            err = "Request failed", f"{type(e).__name__}: {e}"
        except json.JSONDecodeError as e:
            err = "JSON decoding of response failed", e

        handle_error(
            description=err[0],
            exception_details=err[1],
            wait_time=retry_wait_time(current_retries),
            extra_description=f" (attempt {current_retries}/{max_retries})",
        )
        current_retries += 1

    handle_error(description="Maximum number of retries reached", should_exit=True)


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