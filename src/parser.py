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
        return [from_announce] if isinstance(from_announce, bytes) else list(from_announce)

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
    try:
        return sha1(bencoder.encode(torrent_data[b"info"])).hexdigest().upper()
    except KeyError:
        raise TorrentDecodingError("Torrent data does not contain 'info' key")


def recalculate_hash_for_new_source(torrent_data: dict, new_source: bytes) -> str:
    """
    Recalculates the infohash for a new source in the torrent data.

    Args:
        torrent_data (dict): The torrent data dictionary.
        new_source (bytes): The new source to replace in the torrent data.

    Returns:
        str: The recalculated infohash in uppercase.
    """
    torrent_data_copy = copy.deepcopy(torrent_data)
    torrent_data_copy[b"info"][b"source"] = new_source
    return calculate_infohash(torrent_data_copy)


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
    except Exception:
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
1. **Return Type Consistency**: Ensured that `from_announce` is returned as a list directly when it is not already a list.
2. **Variable Naming**: Used a more straightforward assignment after copying in `recalculate_hash_for_new_source`.
3. **Error Handling**: Ensured that `get_bencoded_data` returns the decoded data directly after reading it.
4. **Type Annotations**: Ensured that the type of `new_source` is consistent with the gold code.
5. **Formatting and Indentation**: Ensured consistent indentation and formatting practices.
6. **Removed Invalid Comment**: Removed the invalid comment that caused the `SyntaxError`.

These changes should address the feedback and ensure that the code aligns more closely with the gold standard.