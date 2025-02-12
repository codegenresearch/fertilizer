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


class AuthenticationError(Exception):
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.details = details


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


class RequestHandler:
    def __init__(self, session, timeout: int, rate_limit: int):
        self._s = session
        self._timeout = timeout
        self._rate_limit = rate_limit
        self._last_used = 0
        self._max_retries = 20
        self._max_retry_time = 600
        self._retry_wait_time = lambda x: min(int(exp(x)), self._max_retry_time)

    def make_request(self, url: str, params: dict = None) -> dict:
        current_retries = 1

        while current_retries <= self._max_retries:
            now = time()
            if (now - self._last_used) > self._rate_limit:
                self._last_used = now
                try:
                    response = self._s.get(url, params=params, timeout=self._timeout)
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.HTTPError as e:
                    handle_error(
                        description="HTTP error occurred",
                        exception_details=e,
                        wait_time=self._retry_wait_time(current_retries),
                        extra_description=f" (attempt {current_retries}/{self._max_retries})",
                    )
                except requests.exceptions.Timeout:
                    handle_error(
                        description="Request timed out",
                        wait_time=self._retry_wait_time(current_retries),
                        extra_description=f" (attempt {current_retries}/{self._max_retries})",
                    )
                except requests.exceptions.ConnectionError:
                    handle_error(
                        description="Unable to connect",
                        wait_time=self._retry_wait_time(current_retries),
                        extra_description=f" (attempt {current_retries}/{self._max_retries})",
                    )
                except requests.exceptions.RequestException as e:
                    handle_error(
                        description="Request failed",
                        exception_details=f"{type(e).__name__}: {e}",
                        wait_time=self._retry_wait_time(current_retries),
                        extra_description=f" (attempt {current_retries}/{self._max_retries})",
                    )
                except json.JSONDecodeError as e:
                    handle_error(
                        description="JSON decoding of response failed",
                        exception_details=e,
                        wait_time=self._retry_wait_time(current_retries),
                        extra_description=f" (attempt {current_retries}/{self._max_retries})",
                    )
                current_retries += 1
            else:
                sleep(0.2)

        handle_error(description="Maximum number of retries reached", should_exit=True)