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

  print(f"{Fore.RED}Error {error_code}: {description}{extra_description}. {action}{exception_message}{Fore.RESET}")
  sleep(wait_time)

  if should_exit:
    sys.exit(error_code)


class AuthenticationError(Exception):
  def __init__(self, message, error_code=1001):
    super().__init__(message)
    self.error_code = error_code


class TorrentDecodingError(Exception):
  def __init__(self, message, error_code=1002):
    super().__init__(message)
    self.error_code = error_code


class UnknownTrackerError(Exception):
  def __init__(self, message, error_code=1003):
    super().__init__(message)
    self.error_code = error_code


class TorrentNotFoundError(Exception):
  def __init__(self, message, error_code=1004):
    super().__init__(message)
    self.error_code = error_code


class TorrentAlreadyExistsError(Exception):
  def __init__(self, message, error_code=1005):
    super().__init__(message)
    self.error_code = error_code


class ConfigKeyError(Exception):
  def __init__(self, message, error_code=1006):
    super().__init__(message)
    self.error_code = error_code


class TorrentClientError(Exception):
  def __init__(self, message, error_code=1007):
    super().__init__(message)
    self.error_code = error_code


class TorrentInjectionError(Exception):
  def __init__(self, message, error_code=1008):
    super().__init__(message)
    self.error_code = error_code


def make_request(url, params, timeout=15):
  current_retries = 1
  max_retries = 20
  max_retry_time = 600
  retry_wait_time = lambda x: min(int(exp(x)), max_retry_time)

  while current_retries <= max_retries:
    try:
      response = requests.get(url, params=params, timeout=timeout)
      response.raise_for_status()
      return response.json()
    except requests.exceptions.HTTPError as e:
      err = f"HTTP error occurred: {e}", e
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

  handle_error(description="Maximum number of retries reached", should_exit=True, error_code=1009)