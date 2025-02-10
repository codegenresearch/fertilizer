import sys
from time import sleep

from colorama import Fore


def handle_error(
  description: str,
  exception_details: (str | None) = None,
  wait_time: int = 0,
  extra_description: str = "",
  should_exit: bool = False,
  error_code: int = 1,
) -> None:
  action = "Exiting" if should_exit else "Retrying"
  action += f" in {wait_time} seconds..." if wait_time else "..."
  exception_message = f"\n{Fore.LIGHTBLACK_EX}{exception_details}" if exception_details is not None else ""

  print(f"{Fore.RED}Error: {description}{extra_description}. {action}{exception_message}{Fore.RESET}")
  sleep(wait_time)

  if should_exit:
    sys.exit(error_code)


class AuthenticationError(Exception):
  def __init__(self, message: str, error_code: int = 1001):
    super().__init__(message)
    self.error_code = error_code


class TorrentDecodingError(Exception):
  def __init__(self, message: str, error_code: int = 1002):
    super().__init__(message)
    self.error_code = error_code


class UnknownTrackerError(Exception):
  def __init__(self, message: str, error_code: int = 1003):
    super().__init__(message)
    self.error_code = error_code


class TorrentNotFoundError(Exception):
  def __init__(self, message: str, error_code: int = 1004):
    super().__init__(message)
    self.error_code = error_code


class TorrentAlreadyExistsError(Exception):
  def __init__(self, message: str, error_code: int = 1005):
    super().__init__(message)
    self.error_code = error_code


class ConfigKeyError(Exception):
  def __init__(self, message: str, error_code: int = 1006):
    super().__init__(message)
    self.error_code = error_code


class TorrentClientError(Exception):
  def __init__(self, message: str, error_code: int = 1007):
    super().__init__(message)
    self.error_code = error_code


class TorrentInjectionError(Exception):
  def __init__(self, message: str, error_code: int = 1008):
    super().__init__(message)
    self.error_code = error_code


def make_request(session, url, params, timeout, max_retries, retry_wait_time, error_handler):
    current_retries = 1

    while current_retries <= max_retries:
        try:
            response = session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_handler(
                description=f"Request failed: {e}",
                wait_time=retry_wait_time(current_retries),
                extra_description=f" (attempt {current_retries}/{max_retries})",
            )
            current_retries += 1

    error_handler(description="Maximum number of retries reached", should_exit=True)