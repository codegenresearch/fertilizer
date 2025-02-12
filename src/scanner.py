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
    """\n    Scans a single .torrent file and generates a new one using the tracker API.\n\n    Args:\n      `source_torrent_path` (`str`): The path to the .torrent file.\n      `output_directory` (`str`): The directory to save the new .torrent files.\n      `red_api` (`RedAPI`): The pre-configured RED tracker API.\n      `ops_api` (`OpsAPI`): The pre-configured OPS tracker API.\n      `injector` (`Injection`): The pre-configured torrent Injection object.\n    Returns:\n      str: The path to the new .torrent file.\n    Raises:\n      See `generate_new_torrent_from_file`.\n    """
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

        if injector:
            injector.inject_torrent(
                source_torrent_path,
                new_torrent_filepath,
                new_tracker.site_shortname(),
            )

        return new_torrent_filepath
    except (TorrentDecodingError, UnknownTrackerError, TorrentNotFoundError, TorrentAlreadyExistsError, TorrentExistsInClientError) as e:
        raise e
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")


def __collect_infohashes_from_files(files: list[str]) -> dict:
    infohash_dict = {}

    for filepath in files:
        try:
            torrent_data = get_bencoded_data(filepath)

            if torrent_data:
                infohash = calculate_infohash(torrent_data)
                infohash_dict[infohash] = filepath
        except UnicodeDecodeError:
            continue

    return infohash_dict