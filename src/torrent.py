import os\nimport copy\nfrom html import unescape\nfrom .api import RedAPI, OpsAPI\nfrom .trackers import RedTracker, OpsTracker\nfrom .errors import TorrentDecodingError, UnknownTrackerError, TorrentNotFoundError, TorrentAlreadyExistsError, TorrentExistsInClientError\nfrom .filesystem import replace_extension\nfrom .parser import (\n    get_bencoded_data,\n    get_origin_tracker,\n    recalculate_hash_for_new_source,\n    save_bencoded_data,\n)\ndef generate_new_torrent_from_file(\n    source_torrent_path: str,\n    output_directory: str,\n    red_api: RedAPI,\n    ops_api: OpsAPI,\n    input_infohashes: dict = {},\n    output_infohashes: dict = {},\n) -> tuple[OpsTracker | RedTracker, str, bool]:\n    """\n    Generates a new torrent file for the reciprocal tracker of the original torrent file if it exists on the reciprocal tracker.\n    \\