import os

from .api import RedAPI, OpsAPI
from .filesystem import mkdir_p, list_files_of_extension, assert_path_exists
from .progress import Progress
from .torrent import generate_new_torrent_from_file
from .parser import get_bencoded_data, calculate_infohash
from .errors import (
  TorrentDecodingError,
  UnknownTrackerError,
  TorrentNotFoundError,
  TorrentAlreadyExistsError,
  TorrentExistsInClientError,
)
from .injection import Injection


def scan_torrent_file(
  source_torrent_path: str,
  output_directory: str,
  red_api: RedAPI,
  ops_api: OpsAPI,
  injector: Injection | None,
) -> str:
  """
  Scans a single .torrent file and generates a new one using the tracker API.

  Args:
    `source_torrent_path` (`str`): The path to the .torrent file.
    `output_directory` (`str`): The directory to save the new .torrent files.
    `red_api` (`RedAPI`): The pre-configured RED tracker API.
    `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.
    `injector` (`Injection`): The pre-configured torrent Injection object.
  Returns:
    str: The path to the new .torrent file.
  Raises:
    See `generate_new_torrent_from_file`.
  """
  source_torrent_path = assert_path_exists(source_torrent_path)
  output_directory = mkdir_p(output_directory)

  output_torrents = list_files_of_extension(output_directory, ".torrent")
  output_infohashes = __collect_infohashes_from_files(output_torrents)

  new_tracker, new_torrent_filepath, _ = generate_new_torrent_from_file(
    source_torrent_path,
    output_directory,
    red_api,
    ops_api,
    input_infohashes={},
    output_infohashes=output_infohashes,
  )

  if injector:
    injector.inject_torrent(
      source_torrent_path,
      new_torrent_filepath,
      new_tracker.site_shortname(),
    )

  return new_torrent_filepath


def scan_torrent_directory(
  input_directory: str,
  output_directory: str,
  red_api: RedAPI,
  ops_api: OpsAPI,
  injector: Injection | None,
) -> str:
  """
  Scans a directory for .torrent files and generates new ones using the tracker APIs.

  Args:
    `input_directory` (`str`): The directory containing the .torrent files.
    `output_directory` (`str`): The directory to save the new .torrent files.
    `red_api` (`RedAPI`): The pre-configured RED tracker API.
    `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.
    `injector` (`Injection`): The pre-configured torrent Injection object.
  Returns:
    str: A report of the scan.
  Raises:
    `FileNotFoundError`: if the input directory does not exist.
  """

  input_directory = assert_path_exists(input_directory)
  output_directory = mkdir_p(output_directory)

  input_torrents = list_files_of_extension(input_directory, ".torrent")
  output_torrents = list_files_of_extension(output_directory, ".torrent")
  input_infohashes = __collect_infohashes_from_files(input_torrents)
  output_infohashes = __collect_infohashes_from_files(output_torrents)

  p = Progress(len(input_torrents))

  for i, source_torrent_path in enumerate(input_torrents, 1):
    basename = os.path.basename(source_torrent_path)
    print(f"({i}/{p.total}) {basename}")

    try:
      new_tracker, new_torrent_filepath, was_previously_generated = generate_new_torrent_from_file(
        source_torrent_path,
        output_directory,
        red_api,
        ops_api,
        input_infohashes,
        output_infohashes,
      )

      if injector:
        injector.inject_torrent(
          source_torrent_path,
          new_torrent_filepath,
          new_tracker.site_shortname(),
        )

      if was_previously_generated:
        if injector:
          p.already_exists.print(f"Torrent '{basename}' was previously generated and injected.")
        else:
          p.already_exists.print(f"Torrent '{basename}' was previously generated.")
      else:
        p.generated.print(
          f"Torrent '{basename}' generated as '{new_torrent_filepath}' from '{new_tracker.site_shortname()}'."
        )
    except (TorrentDecodingError, UnknownTrackerError, TorrentNotFoundError, TorrentAlreadyExistsError, TorrentExistsInClientError, Exception) as e:
      p.error.print(f"Error with torrent '{basename}': {str(e)}")

  return p.report()


def __collect_infohashes_from_files(files: list[str]) -> dict:
  infohash_dict = {}

  for filepath in files:
    try:
      torrent_data = get_bencoded_data(filepath)
      if torrent_data:
        infohash = calculate_infohash(torrent_data)
        infohash_dict[infohash] = filepath
    except (UnicodeDecodeError, TorrentDecodingError):
      continue

  return infohash_dict


### Key Changes:
1. **Error Handling**: Simplified the error handling in `scan_torrent_directory` by catching all exceptions in a single block and printing the error message directly.
2. **Output Messages**: Made the output messages more concise and consistent with the expected format in the tests.
3. **Infohash Collection Logic**: Ensured that `torrent_data` is checked before calculating the infohash in `__collect_infohashes_from_files`.
4. **Continue Statements**: Removed unnecessary `continue` statements after handling exceptions.
5. **Formatting and Consistency**: Ensured consistent formatting and readability throughout the code.