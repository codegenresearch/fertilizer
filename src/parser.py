import os
import copy
import bencoder
from hashlib import sha1

from .utils import flatten
from .trackers import RedTracker, OpsTracker
from .errors import TorrentDecodingError


def is_valid_infohash(infohash: str) -> bool:
    """
    Validates if the provided infohash is a valid SHA-1 hash.

    Args:
        infohash (str): The infohash to validate.

    Returns:
        bool: True if the infohash is valid, False otherwise.
    """
    if not isinstance(infohash, str) or len(infohash) != 40:
        return False
    try:
        int(infohash, 16)
        return True
    except ValueError:
        return False


def get_source(torrent_data: dict) -> bytes | None:
    """
    Retrieves the source from the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.

    Returns:
        bytes | None: The source if present, None otherwise.
    """
    try:
        return torrent_data[b"info"][b"source"]
    except KeyError:
        return None


def get_name(torrent_data: dict) -> bytes | None:
    """
    Retrieves the name from the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.

    Returns:
        bytes | None: The name if present, None otherwise.
    """
    try:
        return torrent_data[b"info"][b"name"]
    except KeyError:
        return None


def get_announce_url(torrent_data: dict) -> list[bytes] | None:
    """
    Retrieves the announce URL(s) from the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.

    Returns:
        list[bytes] | None: The announce URL(s) if present, None otherwise.
    """
    from_announce = torrent_data.get(b"announce")
    if from_announce:
        return [from_announce] if isinstance(from_announce, bytes) else from_announce

    from_trackers = torrent_data.get(b"trackers")
    if from_trackers:
        return flatten(from_trackers)

    return None


def get_origin_tracker(torrent_data: dict) -> RedTracker | OpsTracker | None:
    """
    Determines the origin tracker based on the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.

    Returns:
        RedTracker | OpsTracker | None: The origin tracker if identified, None otherwise.
    """
    source = get_source(torrent_data) or b""
    announce_url = get_announce_url(torrent_data) or []

    if source in RedTracker.source_flags_for_search() or any(RedTracker.announce_url() in url for url in announce_url):
        return RedTracker

    if source in OpsTracker.source_flags_for_search() or any(OpsTracker.announce_url() in url for url in announce_url):
        return OpsTracker

    return None


def calculate_infohash(torrent_data: dict) -> str:
    """
    Calculates the infohash of the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.

    Returns:
        str: The calculated infohash in uppercase.

    Raises:
        TorrentDecodingError: If the 'info' key is missing in the torrent data.
    """
    if b"info" not in torrent_data:
        raise TorrentDecodingError("Torrent data does not contain 'info' key")
    return sha1(bencoder.encode(torrent_data[b"info"])).hexdigest().upper()


def recalculate_hash_for_new_source(torrent_data: dict, new_source: bytes) -> str:
    """
    Recalculates the infohash for a new source in the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.
        new_source (bytes): The new source to replace in the torrent data.

    Returns:
        str: The recalculated infohash in uppercase.
    """
    torrent_data[b"info"][b"source"] = new_source
    return calculate_infohash(torrent_data)


def get_bencoded_data(filename: str) -> dict:
    """
    Reads and decodes a bencoded file.

    Args:
        filename (str): The path to the bencoded file.

    Returns:
        dict: The decoded torrent data dictionary if successful, None otherwise.
    """
    try:
        with open(filename, "rb") as f:
            return bencoder.decode(f.read())
    except FileNotFoundError:
        print(f"File not found: {filename}")
    except bencoder.BencodeDecodeError:
        print(f"Error decoding file: {filename}")
    except Exception as e:
        print(f"Unexpected error reading or decoding file {filename}: {e}")
    return None


def save_bencoded_data(filepath: str, torrent_data: dict) -> str:
    """
    Encodes and saves torrent data to a bencoded file.

    Args:
        filepath (str): The path where the file should be saved.
        torrent_data (dict): The torrent data dictionary to encode and save.

    Returns:
        str: The path to the saved file.
    """
    parent_dir = os.path.dirname(filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(bencoder.encode(torrent_data))
    return filepath


### Changes Made:
1. **Error Handling**: Added specific exception handling in `get_bencoded_data` for `FileNotFoundError`, `bencoder.BencodeDecodeError`, and a generic exception for unexpected errors.
2. **Return Types**: Ensured that `from_announce` is checked to be a list before returning it directly.
3. **Use of Exceptions**: Used `TorrentDecodingError` in `calculate_infohash` for clearer error context.
4. **Variable Naming**: Used `announce_url` instead of `announce_urls` for consistency.
5. **Deep Copying**: Simplified `recalculate_hash_for_new_source` by directly modifying `torrent_data`.
6. **File Handling**: Improved exception handling in `get_bencoded_data`.
7. **Directory Creation**: Used `os.makedirs` directly in `save_bencoded_data` to ensure the parent directory is created if it doesn't exist.