import os\nimport copy\nimport bencoder\nfrom hashlib import sha1\nfrom .utils import flatten\nfrom .trackers import RedTracker, OpsTracker\nfrom .errors import TorrentDecodingError\n\ndef is_valid_infohash(infohash: str) -> bool:\n    if not isinstance(infohash, str) or len(infohash) != 40:\n        return False\n    return all(c in '0123456789abcdefABCDEF' for c in infohash)\n\ndef get_source(torrent_data: dict) -> bytes | None:\n    try:\n        return torrent_data[b"info"][b"source"]\n    except KeyError:\n        return None\n\ndef get_name(torrent_data: dict) -> bytes | None:\n    try:\n        return torrent_data[b"info"][b"name"]\n    except KeyError:\n        return None\n\ndef get_announce_url(torrent_data: dict) -> list[bytes] | None:\n    from_announce = torrent_data.get(b"announce")\n    if from_announce:\n        return from_announce if isinstance(from_announce, list) else [from_announce]\n    from_trackers = torrent_data.get(b"trackers")\n    if from_trackers:\n        return flatten(from_trackers)\n    return None\n\ndef get_origin_tracker(torrent_data: dict) -> RedTracker | OpsTracker | None:\n    source = get_source(torrent_data) or b""\n    announce_url = get_announce_url(torrent_data) or []\n\n    if source in RedTracker.source_flags_for_search() or any(RedTracker.announce_url() in url for url in announce_url):\n        return RedTracker\n    if source in OpsTracker.source_flags_for_search() or any(OpsTracker.announce_url() in url for url in announce_url):\n        return OpsTracker\n    return None\n\ndef calculate_infohash(torrent_data: dict) -> str:\n    if b"info" not in torrent_data:\n        raise TorrentDecodingError("Torrent data does not contain 'info' key")\n    return sha1(bencoder.encode(torrent_data[b"info"]))\n           .hexdigest().upper()\n\ndef recalculate_hash_for_new_source(torrent_data: dict, new_source: bytes | str) -> str:\n    torrent_data = copy.deepcopy(torrent_data)\n    torrent_data[b"info"][b"source"] = new_source\n    return calculate_infohash(torrent_data)\n\ndef get_bencoded_data(filename: str) -> dict:\n    try:\n        with open(filename, "rb") as f:\n            data = bencoder.decode(f.read())\n        return data\n    except Exception:\n        return None\n\ndef save_bencoded_data(filepath: str, torrent_data: dict) -> str:\n    parent_dir = os.path.dirname(filepath)\n    if parent_dir:\n        os.makedirs(parent_dir, exist_ok=True)\n    with open(filepath, "wb") as f:\n        f.write(bencoder.encode(torrent_data))\n    return filepath\n