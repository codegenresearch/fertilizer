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
  """\n  Scans a single .torrent file and generates a new one using the tracker API.\n\n  Args:\n    `source_torrent_path` (`str`): The path to the .torrent file.\n    `output_directory` (`str`): The directory to save the new .torrent files.\n    `red_api` (`RedAPI`): The pre-configured RED tracker API.\n    `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.\n    `injector` (`Injection`): The pre-configured torrent Injection object.\n  Returns:\n    str: The path to the new .torrent file.\n  Raises:\n    See `generate_new_torrent_from_file`.\n  """
  source_torrent_path = assert_path_exists(source_torrent_path)
  output_directory = mkdir_p(output_directory)

  output_torrents = list_files_of_extension(output_directory, ".torrent")
  output_infohashes = __collect_infohashes_from_files(output_torrents)

  try:
    new_tracker, new_torrent_filepath, _ = generate_new_torrent_from_file(
      source_torrent_path,
      output_directory,
      red_api,
      ops_api,
      input_infohashes={},
      output_infohashes=output_infohashes,
    )
  except TorrentDecodingError as e:
    raise TorrentDecodingError(f"Error decoding torrent file: {e}")
  except UnknownTrackerError as e:
    raise UnknownTrackerError(f"Unknown tracker: {e}")
  except TorrentNotFoundError as e:
    raise TorrentNotFoundError(f"Torrent not found: {e}")
  except TorrentAlreadyExistsError as e:
    raise TorrentAlreadyExistsError(f"Torrent already exists: {e}")
  except Exception as e:
    raise Exception(f"An unexpected error occurred: {e}")

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
  """\n  Scans a directory for .torrent files and generates new ones using the tracker APIs.\n\n  Args:\n    `input_directory` (`str`): The directory containing the .torrent files.\n    `output_directory` (`str`): The directory to save the new .torrent files.\n    `red_api` (`RedAPI`): The pre-configured RED tracker API.\n    `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.\n    `injector` (`Injection`): The pre-configured torrent Injection object.\n  Returns:\n    str: A report of the scan.\n  Raises:\n    `FileNotFoundError`: if the input directory does not exist.\n  """

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
          p.already_exists.print("Torrent was previously generated but was injected into your torrent client.")
        else:
          p.already_exists.print("Torrent was previously generated.")
      else:
        p.generated.print(
          f"Found with source '{new_tracker.site_shortname()}' and generated as '{new_torrent_filepath}'."
        )
    except TorrentDecodingError as e:
      p.error.print(f"Error decoding torrent file: {e}")
      continue
    except UnknownTrackerError as e:
      p.skipped.print(f"Unknown tracker: {e}")
      continue
    except TorrentAlreadyExistsError as e:
      p.already_exists.print(f"Torrent already exists: {e}")
      continue
    except TorrentExistsInClientError as e:
      p.already_exists.print(f"Torrent exists in client: {e}")
      continue
    except TorrentNotFoundError as e:
      p.not_found.print(f"Torrent not found: {e}")
      continue
    except Exception as e:
      p.error.print(f"An unexpected error occurred: {e}")
      continue

  return p.report()


def __collect_infohashes_from_files(files: list[str]) -> dict:
  infohash_dict = {}

  for filepath in files:
    try:
      torrent_data = get_bencoded_data(filepath)

      if torrent_data:
        if b'info' not in torrent_data:
          raise TorrentDecodingError(f"Missing 'info' key in torrent file: {filepath}")
        infohash = calculate_infohash(torrent_data)
        infohash_dict[infohash] = filepath
    except UnicodeDecodeError:
      continue
    except TorrentDecodingError as e:
      print(f"Error: {e}")
      continue

  return infohash_dict