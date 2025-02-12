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


class RequestHandler:
  def __init__(self, rate_limit, max_retries=20, max_retry_time=600):
    self.rate_limit = rate_limit
    self.max_retries = max_retries
    self.max_retry_time = max_retry_time
    self.last_used = 0
    self.retry_wait_time = lambda x: min(int(exp(x)), self.max_retry_time)

  def make_request(self, session, url, params, timeout=15):
    current_retries = 1

    while current_retries <= self.max_retries:
      now = time()
      if (now - self.last_used) > self.rate_limit:
        self.last_used = now
        try:
          response = session.get(url, params=params, timeout=timeout)
          response.raise_for_status()
          return response.json()
        except requests.exceptions.RequestException as e:
          handle_error(
            description="Request failed",
            exception_details=f"{type(e).__name__}: {e}",
            wait_time=self.retry_wait_time(current_retries),
            extra_description=f" (attempt {current_retries}/{self.max_retries})",
          )
        current_retries += 1
      else:
        sleep(0.2)

    handle_error(description="Maximum number of retries reached", should_exit=True)