import os
import copy
import bencoder
from hashlib import sha1

from .utils import flatten, copy_and_mkdir
from .trackers import RedTracker, OpsTracker


def is_valid_infohash(infohash: str) -> bool:
    """\n    Validates if the provided infohash is a valid SHA-1 hash.\n\n    Args:\n        infohash (str): The infohash to validate.\n\n    Returns:\n        bool: True if the infohash is valid, False otherwise.\n    """
    if not isinstance(infohash, str) or len(infohash) != 40:
        return False
    try:
        int(infohash, 16)
        return True
    except ValueError:
        return False


def get_source(torrent_data: dict) -> bytes | None:
    """\n    Retrieves the source from the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n\n    Returns:\n        bytes | None: The source if present, None otherwise.\n    """
    return torrent_data.get(b"info", {}).get(b"source")


def get_name(torrent_data: dict) -> bytes | None:
    """\n    Retrieves the name from the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n\n    Returns:\n        bytes | None: The name if present, None otherwise.\n    """
    return torrent_data.get(b"info", {}).get(b"name")


def get_announce_url(torrent_data: dict) -> list[bytes] | None:
    """\n    Retrieves the announce URL(s) from the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n\n    Returns:\n        list[bytes] | None: The announce URL(s) if present, None otherwise.\n    """
    from_announce = torrent_data.get(b"announce")
    if from_announce:
        return [from_announce] if isinstance(from_announce, bytes) else from_announce

    from_trackers = torrent_data.get(b"trackers")
    if from_trackers:
        return flatten(from_trackers)

    return None


def get_origin_tracker(torrent_data: dict) -> RedTracker | OpsTracker | None:
    """\n    Determines the origin tracker based on the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n\n    Returns:\n        RedTracker | OpsTracker | None: The origin tracker if identified, None otherwise.\n    """
    source = get_source(torrent_data) or b""
    announce_urls = get_announce_url(torrent_data) or []

    if source in RedTracker.source_flags_for_search() or any(RedTracker.announce_url() in url for url in announce_urls):
        return RedTracker

    if source in OpsTracker.source_flags_for_search() or any(OpsTracker.announce_url() in url for url in announce_urls):
        return OpsTracker

    return None


def calculate_infohash(torrent_data: dict) -> str:
    """\n    Calculates the infohash of the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n\n    Returns:\n        str: The calculated infohash in uppercase.\n\n    Raises:\n        KeyError: If the 'info' key is missing in the torrent data.\n    """
    if b"info" not in torrent_data:
        raise KeyError("Torrent data does not contain 'info' key")
    return sha1(bencoder.encode(torrent_data[b"info"])).hexdigest().upper()


def recalculate_hash_for_new_source(torrent_data: dict, new_source: bytes) -> str:
    """\n    Recalculates the infohash for a new source in the torrent data.\n\n    Args:\n        torrent_data (dict): The torrent data dictionary.\n        new_source (bytes): The new source to replace in the torrent data.\n\n    Returns:\n        str: The recalculated infohash in uppercase.\n    """
    torrent_data_copy = copy.deepcopy(torrent_data)
    torrent_data_copy[b"info"][b"source"] = new_source
    return calculate_infohash(torrent_data_copy)


def get_bencoded_data(filename: str) -> dict:
    """\n    Reads and decodes a bencoded file.\n\n    Args:\n        filename (str): The path to the bencoded file.\n\n    Returns:\n        dict: The decoded torrent data dictionary if successful, None otherwise.\n    """
    try:
        with open(filename, "rb") as f:
            return bencoder.decode(f.read())
    except Exception as e:
        print(f"Error reading or decoding file {filename}: {e}")
        return None


def save_bencoded_data(filepath: str, torrent_data: dict) -> str:
    """\n    Encodes and saves torrent data to a bencoded file.\n\n    Args:\n        filepath (str): The path where the file should be saved.\n        torrent_data (dict): The torrent data dictionary to encode and save.\n\n    Returns:\n        str: The path to the saved file.\n    """
    copy_and_mkdir(filepath)
    with open(filepath, "wb") as f:
        f.write(bencoder.encode(torrent_data))
    return filepath