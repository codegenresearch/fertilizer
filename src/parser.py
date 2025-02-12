import os
import copy
import bencoder
from hashlib import sha1

from .utils import flatten
from .trackers import RedTracker, OpsTracker
from .errors import TorrentDecodingError


def is_valid_infohash(infohash: str) -> bool:
    """Check if the provided infohash is valid."""
    if not isinstance(infohash, str) or len(infohash) != 40:
        return False
    try:
        int(infohash, 16)
        return True
    except ValueError:
        return False


def get_source(torrent_data: dict) -> bytes | None:
    """Retrieve the source from torrent data if available."""
    return torrent_data.get(b"info", {}).get(b"source")


def get_name(torrent_data: dict) -> bytes | None:
    """Retrieve the name from torrent data if available."""
    return torrent_data.get(b"info", {}).get(b"name")


def get_announce_url(torrent_data: dict) -> list[bytes] | None:
    """Retrieve announce URLs from torrent data."""
    from_announce = torrent_data.get(b"announce")
    if from_announce:
        return from_announce if isinstance(from_announce, list) else [from_announce]

    from_trackers = torrent_data.get(b"trackers")
    if from_trackers:
        return flatten(from_trackers)

    return None


def get_origin_tracker(torrent_data: dict) -> RedTracker | OpsTracker | None:
    """Determine the origin tracker based on torrent data."""
    source = get_source(torrent_data) or b""
    announce_urls = get_announce_url(torrent_data) or []

    if source in RedTracker.source_flags_for_search() or any(RedTracker.announce_url() in url for url in announce_urls):
        return RedTracker

    if source in OpsTracker.source_flags_for_search() or any(OpsTracker.announce_url() in url for url in announce_urls):
        return OpsTracker

    return None


def calculate_infohash(torrent_data: dict) -> str:
    """Calculate the infohash of the torrent data."""
    if b"info" not in torrent_data:
        raise TorrentDecodingError("Torrent data does not contain 'info' key")
    return sha1(bencoder.encode(torrent_data[b"info"])).hexdigest().upper()


def recalculate_hash_for_new_source(torrent_data: dict, new_source: bytes | str) -> str:
    """Recalculate the infohash after changing the source in torrent data."""
    new_torrent_data = copy.deepcopy(torrent_data)
    new_torrent_data[b"info"][b"source"] = new_source.encode() if isinstance(new_source, str) else new_source
    return calculate_infohash(new_torrent_data)


def get_bencoded_data(filename: str) -> dict:
    """Read and decode a bencoded file."""
    try:
        with open(filename, "rb") as f:
            return bencoder.decode(f.read())
    except FileNotFoundError:
        raise TorrentDecodingError(f"File not found: {filename}")
    except Exception as e:
        raise TorrentDecodingError(f"Error decoding file {filename}: {str(e)}")


def save_bencoded_data(filepath: str, torrent_data: dict) -> str:
    """Encode and save torrent data to a file."""
    parent_dir = os.path.dirname(filepath)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(filepath, "wb") as f:
            f.write(bencoder.encode(torrent_data))
    except IOError as e:
        raise Exception(f"Error saving file {filepath}: {str(e)}")

    return filepath